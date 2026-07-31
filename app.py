from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from blogger import publish_post
from ai_generator import generate_blog, inject_image_into_blog_and_save_image_to_db
from database import get_images_by_blog, init_db, save_blog
from database import get_all_blogs, update_status, get_blog_by_id
from blogger import publish_post

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

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        topic = request.form.get("topic")
        app.logger.info("Home route accessed")

        if not topic:
            flash("Topic is required!", "error")
            return redirect(url_for("home"))

        try:
            # Generate blog using AI
            title, html_content = generate_blog(topic)
            app.logger.info("Blog generated successfully for topic: %s", topic)

            # Insert image into the blog content
            content = inject_image_into_blog_and_save_image_to_db(html_content, topic)
            app.logger.info("Image injected into blog for topic: %s", topic)

            # Save to database
            save_blog(topic, title, content)
            app.logger.info("Blog saved to database for topic: %s", topic)

            # Publish to Blogger
            # publish_post(title, content)

            flash("AI Blog Generated & Published 🚀", "success")

        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            app.logger.error("Error occurred while generating blog for topic: %s", topic, exc_info=True)

        return redirect(url_for("admin"))

    return render_template("index.html")

@app.route("/admin")
def admin():
    blogs = get_all_blogs()
    return render_template("admin.html", blogs=blogs)

@app.route("/publish/<int:blog_id>")
def publish(blog_id):
    blog = get_blog_by_id(blog_id)

    if not blog:
        return "Blog not found"

    title, content = blog

    try:
        publish_post(title, content)
        update_status(blog_id, "published")
        
    except Exception as e:
        print(e)
        update_status(blog_id, "failed")

    return redirect("/admin")


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
