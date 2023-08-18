from flask import Blueprint, jsonify, request
from movieweb_app.data_managers.sql_data_manager import SQLiteDataManager

api = Blueprint('api', __name__)

@api.route('/users', methods=['GET'])
def get_users():
    data_manager = SQLiteDataManager(api)
    users = data_manager.get_all_users()
    if users:
        users_json = []
        for user in users:
            user_json = {
                "user_id": user.user_id,
                "name": user.name,
                "password": user.password
            }
            users_json.append(user_json)
        return jsonify(users_json)
    return jsonify({"message": "No existing users"}), 404

@api.route('/users/<user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    data_manager = SQLiteDataManager(api)
    user = data_manager.find_user_by_id(user_id)
    if user:
        movies = data_manager.get_user_movies(user_id)
        movies_json = []
        for movie in movies:
            movie_json = {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "director": movie.director,
                "year": movie.year,
                "rating": movie.rating,
                "poster": movie.poster,
                "description": movie.description,
            }
            movies_json.append(movie_json)
        return jsonify(movies_json)
    return jsonify({"message": "User not found"}), 404


@api.route('/users/<user_id>/add_movie', methods=['POST'])
def add_user_movie(user_id):
    data_manager = SQLiteDataManager(api)
    user = data_manager.find_user_by_id(user_id)
    if user:
        request_data = request.json
        movie_title = request_data.get('movie_title')
        if movie_title:
            data_manager.add_user_movie(user_id, movie_title)
            return jsonify({"message": "Movie added successfully"})
        else:
            return jsonify({"message": "Missing movie title in request JSON"}), 400
    else:
        return jsonify({"message": "User not found"}), 404


@api.route('/users/<user_id>/delete_movie/<movie_id>', methods=['POST'])
def delete_user_movie(user_id, movie_id):
    data_manager = SQLiteDataManager(api)
    user = data_manager.find_user_by_id(user_id)
    if user:
        movie_to_delete = data_manager.get_movie_by_id(user_id, movie_id)
        if movie_to_delete:
            data_manager.delete_movie(user_id, movie_id)
            return jsonify({"message": "Movie deleted successfully"})
        else:
            return jsonify({"message": "Missing movie title in request JSON"}), 400
    else:
        return jsonify({"message": "User not found"}), 404


@api.route('/users/<user_id>/update_movie/<movie_id>', methods=['POST'])
def update_user_movie(user_id, movie_id):
    data_manager = SQLiteDataManager(api)
    user = data_manager.find_user_by_id(user_id)
    if user:
        request_data = request.json
        movie_to_update = data_manager.get_movie_by_id(user_id, movie_id)
        movie_title = request_data.get('movie_title')
        if movie_to_update:
            data_manager.update_user_movie(user_id, movie_id, movie_title)
            return jsonify({"message": "Movie updated successfully"})
        else:
            return jsonify({"message": "Missing movie title in request JSON"}), 400
    else:
        return jsonify({"message": "User not found"}), 404


@api.route('/users/<user_id>/movies/<movie_id>/reviews', methods=['GET'])
def get_movie_reviews(user_id, movie_id):
    data_manager = SQLiteDataManager(api)
    user = data_manager.find_user_by_id(user_id)
    if user:
        reviews = data_manager.get_reviews_for_movies(movie_id)
        if reviews:
            reviews_json = []
            for review in reviews:
                review_json = {
                    "review_id": review.review_id,
                    "user_id": review.user.user_id,
                    "movie_id": review.movie_id,
                    "review_text": review.review_text,
                    "user_rating": review.user_rating
                }
                reviews_json.append(review_json)
            return jsonify(reviews_json)
        return jsonify({"message": "No reviews found for this movie"}), 404
    return jsonify({"message": "User not found"}), 404


@api.route('/users/<user_id>/movies/<movie_id>/add_review', methods=['POST'])
def add_movie_review(user_id, movie_id):
    data_manager = SQLiteDataManager(api)
    user = data_manager.find_user_by_id(user_id)
    if user:
        movie = data_manager.get_movie_by_id(user_id, movie_id)
        if movie:
            request_data = request.json
            review_text = request_data.get('review_text')
            user_rating = request_data.get('user_rating')
            if review_text is None or user_rating is None:
                return jsonify({"message": "Missing review_text or user_rating in request JSON"}), 400
            data_manager.add_review(user_id, movie_id, review_text, user_rating)
            return jsonify({"message": "Review added successfully"})
        else:
            return jsonify({"message": "Movie not found for the current user."}), 404
    else:
        return jsonify({"message": "User not found"}), 404


@api.route('/users/<user_id>/movies/<movie_id>/delete_review/<review_id>', methods=['POST'])
def delete_movie_review(user_id, movie_id, review_id):
    data_manager = SQLiteDataManager(api)
    user = data_manager.find_user_by_id(user_id)
    if user:
        movie = data_manager.get_movie_by_id(user_id, movie_id)
        if movie:
            review = data_manager.get_review_by_id(review_id)
            if review:
                if str(review.user.user_id) == user_id:
                    data_manager.delete_review(user_id, review_id)
                    return jsonify({"message": "Review deleted successfully"})
                else:
                    return jsonify({"message": "You can only delete your own reviews."}), 403
            else:
                return jsonify({"message": "Review not found."}), 404
        else:
            return jsonify({"message": "Movie not found for the current user."}), 404
    else:
        return jsonify({"message": "User not found"}), 404


