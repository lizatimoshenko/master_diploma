# from flask import Flask, request, flash, url_for, redirect, render_template, session
# #from app.neo4j_models import User, Book, Tag, add_tag_to_book, add_read_books
# #from app.orientdb_models import User, Book, Tag, add_tag_to_book, add_read_books
# from app.arango_models import User, Book, Tag
# from app import app
# import uuid
#
#
# @app.route('/')
# def hello_world():
#     return render_template("index.html")
#
#
# @app.route("/register", methods=["POST", "GET"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#
#         user = User()
#
#         if not user.register(uuid.uuid1(), password, username):
#             flash("A user with that username already exists.")
#         else:
#             flash("Successfully registered.")
#             return redirect(url_for("login"))
#
#     return render_template("register.html")
#
#
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#
#         user = User()
#
#         if not user.verify_password(password, username):
#             flash("Invalid login.")
#         else:
#             flash("Successfully logged in.")
#             session["username"] = user.username
#             return redirect(url_for("/"))
#
#     return render_template("login.html")
#
#
# @app.route("/get_users")
# # @timing
# def get_users():
#     users = User.get_all_users()
#     return "/"
#
#
# @app.route("/get_tags/<book_id>")
# # @timing
# def get_tags(book_id):
#     tags = Tag.get_tag(book_id)
#
#     # TODO print tags to page
#
#     return "/"
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
