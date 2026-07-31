from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from blogger import publish_post
from ai_generator import generate_blog, inject_image_into_blog_and_save_image_to_db
from database import get_images_by_blog, init_db, save_blog
from database import get_all_blogs, update_status, get_blog_by_id
from blogger import publish_post

init_db()

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        topic = request.form.get("topic")

        if not topic:
            flash("Topic is required!", "error")
            return redirect(url_for("home"))

        try:
            # Generate blog using AI
            title, html_content = generate_blog(topic)

            # Insert image into the blog content
            content = inject_image_into_blog_and_save_image_to_db(html_content, topic)

            # Save to database
            save_blog(topic, title, content)

            # Publish to Blogger
            # publish_post(title, content)

            flash("AI Blog Generated & Published 🚀", "success")

        except Exception as e:
            flash(f"Error: {str(e)}", "error")

        return redirect(url_for("home"))

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
