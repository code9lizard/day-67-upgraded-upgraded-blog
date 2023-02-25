import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    all_blog_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    print(all_blog_posts)
    return render_template("index.html", all_posts=all_blog_posts)


@app.route("/post/<int:index>")
def show_post(index):
    all_blog_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    requested_post = None
    print(index)
    for blog_post in all_blog_posts:
        print(blog_post)
        if blog_post.id == index:
            requested_post = blog_post
    print(requested_post)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    return render_template("contact.html")


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    all_blog_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    print(post_id)
    for blog_post in all_blog_posts:
        if blog_post.id == post_id:
            edit_form = CreatePostForm(title=blog_post.title,
                                       subtitle=blog_post.subtitle,
                                       author=blog_post.author,
                                       img_url=blog_post.img_url,
                                       body=blog_post.body)
            if edit_form.validate_on_submit():
                blog_post.title = edit_form.title.data
                blog_post.subtitle = edit_form.subtitle.data
                blog_post.author = edit_form.author.data
                blog_post.img_url = edit_form.img_url.data
                blog_post.body = edit_form.body.data
                db.session.commit()
                return redirect(url_for("get_all_posts"))
            return render_template("make-post.html", method_name="Edit Post", form=edit_form)


@app.route("/new-post", methods=["GET", "POST"])
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        now = datetime.datetime.now()
        new_post = BlogPost(title=form.title.data,
                            subtitle=form.subtitle.data,
                            date=now.strftime("%B %w, %Y"),
                            body=form.body.data,
                            author=form.author.data,
                            img_url=form.img_url.data)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, method_name="New Post")


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    all_blog_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    for blog_post in all_blog_posts:
        if blog_post.id == post_id:
            db.session.delete(blog_post)
            db.session.commit()
    return redirect(url_for("get_all_posts"))


if __name__ == "__main__":
    app.run(debug=True)
