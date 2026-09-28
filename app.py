from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from blogger import (
    ReauthRequired,
    begin_authorization,
    finish_authorization,
    publish_post,
)
from ai_generator import generate_blog, inject_image_into_blog_and_save_image_to_db
from database import get_images_by_blog, init_db, save_blog
from database import get_all_blogs, update_status, get_blog_by_id, get_statuses_by_topic
from trending import get_top_trends

import logging
from logging.config import dictConfig

import database
import ai_generator


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        },
        'file': {  # <-- Add this FileHandler
            'class': 'logging.FileHandler',
            'filename': 'app.log', # This will create 'app.log' in your root folder
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
})


init_db()

app = Flask(__name__)
app.config.from_object(Config)

def _generate_and_save(topic):
    title, html_content = generate_blog(topic)
    content = inject_image_into_blog_and_save_image_to_db(html_content, topic)
    save_blog(topic, title, content)
    return title


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        topic = request.form.get("topic")
        app.logger.info("Home route accessed")

        if not topic:
            flash("Topic is required!", "error")
            return redirect(url_for("home"))

        try:
            _generate_and_save(topic)
            app.logger.info("Blog saved to database for topic: %s", topic)
            flash("AI Blog Generated & Published 🚀", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            app.logger.error("Error occurred while generating blog for topic: %s", topic, exc_info=True)

        return redirect(url_for("admin"))

    return render_template("index.html")


def _mark_trend_flags(groups):
    keywords = [
        trend["keyword"]
        for group in groups
        for trend in group["trends"]
    ]
    statuses = get_statuses_by_topic(keywords)
    for group in groups:
        for trend in group["trends"]:
            status = statuses.get(trend["keyword"].strip().lower())
            trend["generated"] = status is not None
            trend["posted"] = status == "published"


@app.route("/trends", methods=["GET", "POST"])
def trends():
    if request.method == "POST":
        selected = []
        for topic in request.form.getlist("topics"):
            topic = (topic or "").strip()
            if topic and topic not in selected:
                selected.append(topic)
        selected = selected[:10]

        if not selected:
            flash("Select at least one trend to generate.", "error")
            return redirect(url_for("trends"))

        created = 0
        failed = []
        for topic in selected:
            try:
                _generate_and_save(topic)
                created += 1
                app.logger.info("Blog saved from trend: %s", topic)
            except Exception as exc:
                failed.append(topic)
                app.logger.error(
                    "Trend generation failed for %s: %s", topic, type(exc).__name__
                )

        if created:
            flash(
                f"Generated {created} blog(s). Publish the ones you want from this page.",
                "success",
            )
        if failed:
            flash("Could not generate: " + ", ".join(failed), "error")
        return redirect(url_for("admin"))

    groups = []
    for geo, label in (("IN", "India"), ("US", "United States")):
        try:
            items = get_top_trends(geo, limit=5)
            groups.append({"label": label, "trends": items, "error": None})
        except Exception as exc:
            app.logger.error("Trend fetch failed for %s: %s", geo, type(exc).__name__)
            groups.append({
                "label": label,
                "trends": [],
                "error": f"Could not load {label} trends.",
            })

    _mark_trend_flags(groups)
    return render_template("trends.html", groups=groups)

@app.route("/admin")
def admin():
    blogs = get_all_blogs()
    return render_template("admin.html", blogs=blogs)

def _clear_oauth_session():
    for key in ("oauth_state", "oauth_redirect_uri", "oauth_code_verifier", "oauth_blog_id"):
        session.pop(key, None)


def _start_google_auth(blog_id):
    session.pop("oauth_resumed", None)
    redirect_uri = url_for("oauth2callback", _external=True)
    authorization_url, state, code_verifier = begin_authorization(redirect_uri)
    session["oauth_state"] = state
    session["oauth_redirect_uri"] = redirect_uri
    session["oauth_code_verifier"] = code_verifier
    session["oauth_blog_id"] = blog_id
    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    if request.args.get("error"):
        _clear_oauth_session()
        flash("Google sign-in was cancelled.", "error")
        return redirect(url_for("admin"))

    state = session.get("oauth_state")
    redirect_uri = session.get("oauth_redirect_uri")
    code_verifier = session.get("oauth_code_verifier")
    blog_id = session.get("oauth_blog_id")

    if not state or state != request.args.get("state") or not redirect_uri or not code_verifier:
        _clear_oauth_session()
        flash("Google sign-in could not be verified. Try publishing again.", "error")
        return redirect(url_for("admin"))

    try:
        finish_authorization(redirect_uri, request.url, state, code_verifier)
    except Exception as exc:
        app.logger.error("Google token exchange failed: %s", type(exc).__name__)
        _clear_oauth_session()
        flash("Google sign-in failed. Try publishing again.", "error")
        return redirect(url_for("admin"))

    _clear_oauth_session()
    session["oauth_resumed"] = True
    if not blog_id:
        return redirect(url_for("admin"))
    return redirect(url_for("publish", blog_id=blog_id))


@app.route("/publish/<int:blog_id>")
def publish(blog_id):
    blog = get_blog_by_id(blog_id)

    if not blog:
        return "Blog not found"

    title, content = blog

    try:
        publish_post(title, content)
        update_status(blog_id, "published")
    except ReauthRequired:
        if session.pop("oauth_resumed", False):
            flash("Google sign-in completed, but publishing still failed.", "error")
            return redirect(url_for("admin"))
        app.logger.info("Redirecting to Google to refresh Blogger credentials for blog %s", blog_id)
        return _start_google_auth(blog_id)
    except Exception as exc:
        app.logger.error("Publish failed for blog %s: %s", blog_id, type(exc).__name__)
        update_status(blog_id, "failed")

    return redirect(url_for("admin"))

@app.route("/preview/<int:blog_id>")
def preview(blog_id):
    blog = get_blog_by_id(blog_id)
    images = get_images_by_blog(blog_id)

    title, content = blog

    return render_template(
        "preview.html",
        title=title,
        content=content,
        images=images   # 👈 IMPORTANT
    )


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
