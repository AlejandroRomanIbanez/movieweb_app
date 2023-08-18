import requests
import json
import time
from movieweb_app.data_managers.data_manager_interface import DataManagerInterface


class JSONDataManager(DataManagerInterface):
    """
        DataManager implementation using a JSON file for data storage.
    """
    def __init__(self, filename):
        self.filename = filename
        self.api_key = "eaf9a303"
        self.request_url = "http://www.omdbapi.com/?apikey={}&t=".format(self.api_key)

    def open_file(self):
        """
        Opens the JSON file and returns its content as a dictionary.
        Returns:
            dict: The content of the JSON file as a dictionary.
        """
        with open(self.filename, "r") as file:
            data_file = json.load(file)
        return data_file

    def save_file(self, data):
        """
        Saves the provided data dictionary to the JSON file.
        Args:
            data (dict): The data to be saved to the JSON file.
        """
        with open(self.filename, "w") as file:
            data_file = json.dump(data, file, indent=4)
        return data_file

    def get_movie_info(self, movie_name):
        """
        Retrieves movie information from the OMDb API based on the movie name.
        Args:
            movie_name (str): The name of the movie.
        Returns:
            dict or None: The movie information as a dictionary if found, None otherwise.
        """
        response = requests.get(self.request_url + movie_name)
        if response.status_code == 200:
            movie_info = response.json()
            if movie_info['Response'] == 'False':
                return None
            return movie_info
        else:
            print("Error occurred while retrieving movie information.")
            return None

    def register_user(self, username, password):
        """
        Registers a new user with the provided username and password.
        Args:
            username (str): The username of the new user.
            password (str): The password of the new user.
        """
        data = self.open_file()
        user_ids = self.get_all_users_id()
        new_id = max(user_ids) + 1 if user_ids else 1
        data[str(new_id)] = {'name': username, 'password': password, 'movies': []}
        self.save_file(data)

    def check_user_password(self, user_id, password):
        """
        Checks if the provided password matches the user's password.
        Args:
            user_id (str): The ID of the user.
            password (str): The password to check.
        Returns:
            bool: True if the password matches, False otherwise.
        """
        user = self.find_user_by_id(user_id)
        if user and user['password'] == password:
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
        data = self.open_file()
        return data.get(user_id, None)

    def get_all_users(self):
        """
        Returns a list of all usernames.
        Returns:
            list: A list of all usernames.
        """
        info = self.open_file()
        users = [user['name'] for user in info.values()]
        return users

    def get_user_movies(self, user_id):
        """
        Returns a list of movies for a given user ID.
        Args:
            user_id (str): The ID of the user.
        Returns:
            list or str: A list of movies if the user is found and has movies, or a string indicating no movies.
        """
        user = self.find_user_by_id(user_id)
        if user:
            return user['movies']
        return "User has no movies"

    def get_all_users_id(self):
        """
        Returns a list of all user IDs.
        Returns:
            list: A list of all user IDs.
        """
        data = self.open_file()
        return [int(user_id) for user_id in data.keys()]

    def add_user_movie(self, user_id, name):
        """
        Adds a movie to the user's movie list based on the provided movie name.
        Args:
            user_id (str): The ID of the user.
            name (str): The name of the movie to add.
        """
        data = self.open_file()
        user = self.find_user_by_id(user_id)
        if user:
            movie_info = self.get_movie_info(name)
            if movie_info is None:
                print("This movie doesn't exist. Make sure you write it correctly.")
                return
            movies = user['movies']
            new_movie_id = f"{user_id}_{int(time.time())}"
            new_movie = {
                'movie_id': new_movie_id,
                'title': movie_info['Title'],
                'director': movie_info['Director'],
                'year': int(movie_info['Year']),
                'rating': float(movie_info['imdbRating']),
                'poster': movie_info['Poster']
            }
            movies.append(new_movie)
            user['movies'] = movies
            data[str(user_id)] = user
            self.save_file(data)
        else:
            print("User not found.")

    def get_movie_by_id(self, user_id, movie_id):
        """
        Retrieves and returns a movie dictionary based on the user ID and movie ID.
        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.
        Returns:
            dict or None: The movie dictionary if found, None otherwise.
        """
        user = self.find_user_by_id(user_id)
        if user:
            movies = user['movies']
            for movie in movies:
                if movie['movie_id'] == movie_id:
                    return movie

    def update_user_movie(self, user_id, movie_id, name, rating):
        """
        Updates movie details based on the provided information.
        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie to update.
            name (str): The new name of the movie.
            rating (float): The new rating of the movie.
        """
        data = self.open_file()
        user = self.find_user_by_id(user_id)
        if user:
            movie = self.get_movie_by_id(user_id, movie_id)
            if movie:
                if name != movie['title']:
                    movie_info = self.get_movie_info(name)
                    if movie_info is None:
                        print("This movie doesn't exist. Make sure you write it correctly.")
                        return
                    new_movie = {
                        'movie_id': movie_id,
                        'title': movie_info['Title'],
                        'director': movie_info['Director'],
                        'year': int(movie_info['Year']),
                        'rating': float(movie_info['imdbRating']),
                        'poster': movie_info['Poster']
                    }
                    movies = user['movies']
                    updated_movies = [new_movie if movie['movie_id'] == movie_id else movie for movie in movies]
                    user['movies'] = updated_movies
                else:
                    movies = user['movies']
                    if 0 <= float(rating) <= 10:
                        movie['rating'] = float(rating)
                        update_movie = movie
                        updated_movies = [update_movie if movie['movie_id'] == movie_id else movie for movie in movies]
                        user['movies'] = updated_movies
                    else:
                        print("Invalid rating. The maximum rating allowed is 10.")
                        return
                data[str(user_id)] = user
                self.save_file(data)
            else:
                print("Movie not found.")
        else:
            print("User not found.")

    def delete_movie(self, user_id, movie_id):
        """
        Deletes a movie from the user's movie list based on the user ID and movie ID.
        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie to delete.
        Returns:
            list or None: The list of remaining movies if the movie is found and deleted, None otherwise.
        """
        data = self.open_file()
        user = self.find_user_by_id(user_id)
        movie = self.get_movie_by_id(user_id, movie_id)
        if movie:
            movies = user['movies']
            user['movies'] = [movie for movie in movies if movie['movie_id'] != movie_id]
            data[str(user_id)] = user
            self.save_file(data)
            return movies
        else:
            print("Movie not found.")

    def login(self, username, password):
        """
        Authenticates a user based on the provided username and password.
        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        Returns:
            str or None: The ID of the authenticated user if credentials are valid, None otherwise.
        """
        data = self.open_file()
        for user_id, user in data.items():
            if user['name'] == username and user['password'] == password:
                return user_id
        return None
