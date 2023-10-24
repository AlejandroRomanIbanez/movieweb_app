from movieweb_app.data_managers.data_manager_interface import DataManagerInterface
from movieweb_app.data_models.data_models import db
from movieweb_app.data_models.data_models import User, Movie, Review
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import random
import re


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, database_path):
        self.db = db
        self.api_key = "API KEY HERE"
        self.request_url = "http://www.omdbapi.com/?apikey={}&t=".format(self.api_key)

    def update_user_profile(self, user_id, new_name, new_password, profile_picture=None):
        user = self.db.session.query(User).get(user_id)
        if user:
            if new_name:
                user.name = new_name
            if new_password:
                user.password = generate_password_hash(new_password)
            if profile_picture:
                user.profile_picture = profile_picture
            self.db.session.commit()

    def get_most_popular_movies(self):
        url = "https://google-bard1.p.rapidapi.com/"
        headers = {
            "text": "Most 10 popular movies of this week?Just write the titles like this: 1.Batman, 2.Scream (until 10)",
            "lang": "en",
            "psid": "PSID-1 HERE",
            "X-RapidAPI-Key": "API KEY HERE",
            "X-RapidAPI-Host": "google-bard1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(response_data)
                popular_movies = re.findall(r'\d+\.\s+(.+)', response_data['response'])
                print(popular_movies)
                if popular_movies:
                    return popular_movies
                else:
                    print("No popular movies found in the response.")
                    return None
            except Exception as e:
                print("Error occurred while parsing JSON response:", str(e))
                return None
        else:
            print("Error ocurred while fetching most popular movies")

    def recommend_popular_movie(self):
        popular_movies = self.get_most_popular_movies()
        if popular_movies:
            random_movie = random.choice(popular_movies)
            return random_movie
        else:
            return None

    def get_movie_info(self, movie_name):
        """
        Retrieves movie information from the OMDb API based on the movie name.
        Args:
            movie_name (str): The name of the movie.
        Returns:
            dict or None: The movie information as a dictionary if found, None otherwise.
        """
        if movie_name:
            response = requests.get(self.request_url + movie_name)
            if response.status_code == 200:
                movie_info = response.json()
                if movie_info['Response'] == 'False':
                    return None
                return movie_info
            else:
                print("Error occurred while retrieving movie information.")
                return None

    def delete_review(self, user_id, review_id):
        user = self.db.session.query(User).get(user_id)
        if user:
            review = self.db.session.query(Review).get(review_id)
            if review:
                if review.user.user_id == user_id:
                    self.db.session.delete(review)
                    self.db.session.commit()
                    print("Review deleted successfully.")
                else:
                    print("You can only delete your own reviews.")
            else:
                print("Review not found.")
        else:
            print("User not found.")

    def add_review(self, user_id, movie_id, review_text, user_rating):
        user = self.db.session.query(User).get(user_id)
        movie = self.db.session.query(Movie).get(movie_id)
        if user and movie:
            new_review = Review(
                user=user,
                movie=movie,
                review_text=review_text,
                user_rating=user_rating
            )
            self.db.session.add(new_review)
            self.db.session.commit()
        else:
            print("User or Movie not found.")

    def register_user(self, username, password):
        """
        Registers a new user with the provided username and password.
        Args:
            username (str): The username of the new user.
            password (str): The password of the new user.
        """
        user_ids = self.get_all_users_id()
        new_id = max(user_ids) + 1 if user_ids else 1
        hashed_password = generate_password_hash(password)
        new_user = User(user_id=new_id, name=username, password=hashed_password)
        self.db.session.add(new_user)
        self.db.session.commit()

    def find_user_by_name(self, name):
        user = self.db.session.query(User).filter_by(name=name).first()
        return user

    def check_user_password(self, username, password):
        """
        Checks if the provided password matches the user's password.
        Args:
            user_id (str): The ID of the user.
            password (str): The password to check.
        Returns:
            bool: True if the password matches, False otherwise.
        """
        user = self.find_user_by_name(username)
        if user and check_password_hash(user.password, password):
            return True
        return False

    def find_user_by_id(self, user_id):
        """
        Finds and returns a user dictionary based on the user ID.
        Args:
            user_id (str): The ID of the user.
        Returns:
            dict or None: The user dictionary if found, None otherwise.
        """
        user = self.db.session.query(User).get(user_id)
        return user

    def get_all_users_id(self):
        """
        Returns a list of all user IDs.
        Returns:
            list: A list of all user IDs.
        """
        users = self.db.session.query(User).all()
        return [int(user.user_id) for user in users]

    def get_all_users_names(self):
        users = self.db.session.query(User).all()
        usernames = [user.name for user in users]
        return usernames

    def get_all_users(self):
        users = self.db.session.query(User).all()
        return users

    def get_user_movies(self, user_id):
        user = self.db.session.query(User).get(user_id)
        if user:
            return user.movies
        return "User has no movies"

    def add_user_movie(self, user_id, name):
        user = self.db.session.query(User).get(user_id)
        if user:
            existing_movie = self.db.session.query(Movie).filter_by(title=name).first()
            if existing_movie:
                user.movies.append(existing_movie)
            else:
                movie_info = self.get_movie_info(name)
                if movie_info is None:
                    print("This movie doesn't exist. Make sure you write it correctly.")
                    return
                imdb_rating = movie_info.get('imdbRating')
                alternative_rating = movie_info.get('Ratings', [])

                if imdb_rating and imdb_rating != "N/A":
                    try:
                        imdb_rating = float(imdb_rating)
                    except ValueError:
                        imdb_rating = "N/A"
                else:
                    imdb_rating = "N/A"

                if imdb_rating == "N/A":
                    for rating_entry in alternative_rating:
                        if 'Internet Movie Database' in rating_entry.get('Source', ''):
                            alternative_imdb_rating = rating_entry.get('Value', '').strip()
                            if alternative_imdb_rating:
                                try:
                                    imdb_rating = float(alternative_imdb_rating)
                                    break
                                except Exception as e:
                                    print("Error: {e}")
                    else:
                        imdb_rating = "N/A"
                new_movie = Movie(
                    title=movie_info['Title'],
                    director=movie_info['Director'],
                    year=int(movie_info['Year']),
                    rating=imdb_rating,
                    poster=movie_info['Poster'],
                    description=movie_info.get('Plot', '')
                )
                user.movies.append(new_movie)
            self.db.session.commit()
        else:
            print("User not found")

    def get_reviews_for_movies(self, movie_id):
        reviews = self.db.session.query(Review).filter_by(movie_id=movie_id).all()
        if reviews:
            return reviews

    def get_review_by_id(self, review_id):
        return self.db.session.query(Review).get(review_id)

    def get_movie_by_id(self, user_id, movie_id):
        """
        Retrieves and returns a movie dictionary based on the user ID and movie ID.
        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.
        Returns:
            dict or None: The movie dictionary if found, None otherwise.
        """
        user = self.db.session.query(User).get(user_id)
        if user:
            movies = user.movies
            for movie in movies:
                if str(movie.movie_id) == movie_id:
                    return movie

    def update_user_movie(self, user_id, movie_id, name):
        user = self.db.session.query(User).get(user_id)
        if user:
            movie = self.get_movie_by_id(user_id, movie_id)
            if movie:
                old_movie_reviews = self.db.session.query(Review).filter_by(movie_id=movie_id).all()
                user.movies.remove(movie)
                new_movie = self.db.session.query(Movie).filter_by(title=name).first()
                if new_movie:
                    user.movies.append(new_movie)
                else:
                    movie_info = self.get_movie_info(name)
                    if movie_info is None:
                        print("This movie doesn't exist. Make sure you write it correctly.")
                        return
                    new_movie = Movie(
                        title=movie_info['Title'],
                        director=movie_info['Director'],
                        year=int(movie_info['Year']),
                        rating=float(movie_info['imdbRating']),
                        poster=movie_info['Poster'],
                        description=movie_info.get('Plot', '')
                    )
                    user.movies.append(new_movie)
                if len(movie.users) == 0:
                    self.db.session.delete(movie)
                    for review in old_movie_reviews:
                        self.db.session.delete(review)
                self.db.session.commit()
            else:
                print("Movie not found for the current user.")
        else:
            print("User not found.")

    def delete_movie(self, user_id, movie_id):
        user = self.db.session.query(User).get(user_id)
        if user:
            movie = self.get_movie_by_id(user_id, movie_id)
            if movie:
                if len(movie.users) > 1:
                    user.movies.remove(movie)
                else:
                    reviews_to_delete = self.db.session.query(Review).filter_by(movie_id=movie_id).all()
                    for review in reviews_to_delete:
                        self.db.session.delete(review)
                    self.db.session.delete(movie)
                self.db.session.commit()
                movies = self.get_user_movies(user_id)
                return movies
            else:
                print("Movie not found.")
        else:
            print("User not found.")

    def login(self, username, password):
        """
        Authenticates a user based on the provided username and password.
        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        Returns:
            str or None: The ID of the authenticated user if credentials are valid, None otherwise.
        """
        user = self.db.session.query(User).filter_by(name=username, password=password).first()
        if user:
            return user.user_id
        return None

