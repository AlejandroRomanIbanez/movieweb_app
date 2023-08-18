from flask import Flask, render_template, request, redirect, url_for, session, flash
from movieweb_app.data_models import data_models
# from data_managers.json_data_manager import JSONDataManager
from movieweb_app.data_models.data_models import db
from movieweb_app.data_managers.sql_data_manager import SQLiteDataManager
from movieweb_app.blueprints.api_routes import api
import os
import secrets


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.secret_key = secrets.token_hex(16)
database_path = os.path.join(app.root_path, 'data', 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
db.init_app(app)
data_manager = SQLiteDataManager(app)

@app.errorhandler(400)
def handle_value_error(error):
    """
    Page for handling ValueError.
    Args:
        error (Exception): The ValueError instance.
    Returns:
        flask.Response: The rendered template for the 400 error page.
    """
    return render_template('value_error.html', error=error), 400


@app.errorhandler(404)
def page_not_found(error):
    """
    Page for displaying 404 errors.
    Args:
        error (Exception): The 404 error instance.
    Returns:
        flask.Response: The rendered template for the 404 error page.
    """
    return render_template('404.html', error=error), 404


@app.errorhandler(401)
def forbidden_access(error):
    """
    Page for displaying 401 errors.
    Args:
        error (Exception): The 401 error instance.
    Returns:
        flask.Response: The rendered template for the 401 error page.
    """
    return render_template('401.html', error=error), 401


@app.route('/')
def home():
    """
    Home page route.
    Returns:
        flask.Response: The rendered template for the home page.
    """
    return render_template('home.html')


@app.route('/login', methods=['POST'])
def login():
    """
    Login route.
    Returns:
        flask.Response: The rendered template based on the login result.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    user_id = data_manager.login(username, password)
    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('user_movies', user_id=user_id))
    else:
        return render_template('home.html', error='Invalid credentials', username=username)


@app.route('/logout')
def logout():
    """
    Logout route.
    Returns:
        flask.Response: A redirect response to the home page.
    """
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/users')
def list_users():
    """
    List users route.
    Returns:
        flask.Response: The rendered template for listing all users.
    """
    users = data_manager.get_all_users_names()
    return render_template('users.html', users=users)


@app.route('/users/<user_id>', methods=['GET', 'POST'])
def user_authorization(user_id):
    """
    User authorization route.
    Returns:
        flask.Response: The rendered template based on the authorization result.
    """
    if request.method == 'POST':
        password = request.form.get('password')
        user = data_manager.find_user_by_id(user_id)
        if user and data_manager.check_user_password(user_id, password):
            session['user_id'] = user_id
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            return render_template('users.html', users=data_manager.get_all_users_names(), error='Invalid password')
    return render_template('users.html', users=data_manager.get_all_users_names())


@app.route('/users/<user_id>/movies')
def user_movies(user_id):
    """
    User movies route.
    Returns:
        flask.Response: The rendered template for the user's movies.
    """
    if 'user_id' in session and session['user_id'] == user_id:
        user = data_manager.find_user_by_id(user_id)
        if user:
            movies = data_manager.get_user_movies(user_id)
            return render_template('movies.html', movies=movies, user_id=user_id)
    return render_template('404.html', error='User not found'), 404


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Add user route.
    Returns:
        flask.Response: A redirect response to list all users after adding a new user.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        data_manager.register_user(username, password)
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<user_id>/recommend_movie', methods=['GET'])
def recommend_movie(user_id):
    user = data_manager.find_user_by_id(user_id)
    try:
        if user:
            recommended_movie = data_manager.recommend_popular_movie()
            movie = data_manager.get_movie_info(recommended_movie)
            if movie:
                return render_template('recommended_movie.html', user=user, movie=movie)
            else:
                flash('No popular movies found for recommendation.', 'info')
                return redirect(url_for('user_movies', user_id=user_id))
        else:
            return render_template('404.html', error='User not found'), 404
    except TypeError as e:
        return f"Error {e}"


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movies(user_id):
    """
    Add movie route.
    Returns:
        flask.Response: The rendered template for adding a movie or a redirect response after adding a movie.
    """
    if 'user_id' in session and session['user_id'] == user_id:
        if request.method == 'POST':
            name = request.form.get('name')
            data_manager.add_user_movie(user_id, name)
            return redirect(url_for('user_movies', user_id=user_id)), 201
        return render_template('add_movie.html', user_id=user_id)
    return redirect(url_for('home'))


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Update movie route.
    Returns:
        flask.Response: The rendered template for updating a movie or a redirect response after updating a movie.
    """
    if 'user_id' in session and session['user_id'] == user_id:
        if request.method == 'POST':
            try:
                name = request.form.get('name')
                data_manager.update_user_movie(user_id, movie_id, name)
                return redirect(url_for('user_movies', user_id=user_id))
            except ValueError as ve:
                print("ValueError occurred:", ve)
                return render_template('400.html', error="You can only use a float number for the rating"), 400
        else:
            movie = data_manager.get_movie_by_id(user_id, movie_id)
            if movie:
                return render_template('update_movie.html', movie=movie, user_id=user_id, movie_id=movie_id)
    return redirect(url_for('home'))


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    """
    Delete movie route.
    Returns:
        flask.Response: The rendered template for deleting a movie or a redirect response after deleting a movie.
    """
    if 'user_id' in session and session['user_id'] == user_id:
        movie = data_manager.get_movie_by_id(user_id, movie_id)
        if movie:
            if request.method == 'POST':
                data_manager.delete_movie(user_id, movie_id)
                return redirect(url_for('user_movies', user_id=user_id))
            return render_template('delete_movie.html', user_id=user_id, movie_id=movie_id)
    return redirect(url_for('home'))


@app.route('/users/<user_id>/delete_review/<review_id>', methods=['GET', 'POST'])
def delete_review(user_id, review_id):
    if 'user_id' in session and session['user_id'] == user_id:
        review = data_manager.get_review_by_id(review_id)
        if review:
            if request.method == 'POST':
                data_manager.delete_review(user_id, review_id)
                return redirect(url_for('user_movies', user_id=user_id))
            return render_template('delete_review.html', user_id=user_id, review_id=review_id)
    return redirect(url_for('home'))


@app.route('/<user_id>/add_review/<movie_id>', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    if request.method == 'POST':
        review_text = request.form.get('review_text')
        user_rating = float(request.form.get('user_rating'))
        user = data_manager.find_user_by_id(user_id)
        movie = data_manager.get_movie_by_id(user_id, movie_id)
        if user and movie:
            existing_reviews = data_manager.get_reviews_for_movies(movie_id)
            if existing_reviews is None:
                data_manager.add_review(user_id, movie_id, review_text, user_rating)
                flash('Review submitted successfully!', 'success')
            else:
                user_reviewed = any(str(review.user.user_id) == user_id for review in existing_reviews)
                if user_reviewed:
                    flash('You have already reviewed this movie.', 'warning')
                else:
                    data_manager.add_review(user_id, movie_id, review_text, user_rating)
                    flash('Review submitted successfully!', 'success')
            return redirect(url_for('movie_detail', user_id=user_id, movie_id=movie_id))
        else:
            return "User or Movie not found"
    else:
        return render_template('add_review.html', user_id=user_id, movie_id=movie_id)


@app.route('/<user_id>/movie_detail/<movie_id>', methods=['GET', 'POST'])
def movie_detail(user_id, movie_id):
    """
    Movie detail route.
    Returns:
        flask.Response: The rendered template for the movie detail page.
    """
    user = data_manager.find_user_by_id(user_id)
    movie = data_manager.get_movie_by_id(user_id, movie_id)
    if user and movie:
        reviews = data_manager.get_reviews_for_movies(movie_id)
        all_users = data_manager.get_all_users_names()
        return render_template('movie_detail.html', user=user, movie=movie, reviews=reviews, all_users=all_users)
    return render_template('404.html', error='Movie not found'), 404





if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        data_models.print_all_data()
    app.run(debug=True)

