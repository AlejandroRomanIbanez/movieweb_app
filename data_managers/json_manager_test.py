import pytest
from movieweb_app.data_managers.json_data_manager import JSONDataManager


data_manager = JSONDataManager('../tests/test.json')

def test_get_all_users():
    users = data_manager.get_all_users()
    assert isinstance(users, list)
    assert len(users) == 2  # Assuming there are two users in the test data

def test_get_user_movies():
    movies = data_manager.get_user_movies('1')  # Assuming user ID 1 exists in the test data
    assert isinstance(movies, list)

def test_add_new_user():
    data_manager.register_user("John Doe", "pass")
    users = data_manager.get_all_users()
    assert len(users) == 3  # Assuming that was only 2 users

def test_add_user_movie():
    data_manager.add_user_movie('3', "Titanic")  # Assuming user ID '3' exists in the test data
    movies = data_manager.get_user_movies('3')  # Assuming user ID '3' exists in the test data
    assert len(movies) == 1  # Assuming the first movie is added

def test_update_user_movie():
    data_manager.update_user_movie('1', "1_1689246388", "Scream 2", 8.5)  # Assuming user ID 1 and movie ID "1_1689246388" exist in the test data
    movie = data_manager.get_movie_by_id('1', "1_1689246388")  # Assuming user ID 1 and movie ID "1_1689246388" exist in the test data
    assert movie['name'] == "Scream 2"

def test_delete_movie():
    data_manager.delete_movie('2', "2_1689246182")  # Assuming user ID '2' and movie ID "2_1689246182" exist in the test data
    movies = data_manager.get_user_movies('2')
    assert len(movies) == 0  # Assuming it was only 1 movie

def test_get_non_existing_user_movies():
    movies = data_manager.get_user_movies('100')  # Assuming user ID '100' does not exist in the test data
    assert movies == "User has no movies"

def test_get_non_existing_movie():
    movie = data_manager.get_movie_by_id('1', "non_existing_id")  # Assuming user ID '1' exists in the test data
    assert movie is None

def test_get_non_existing_user():
    user = data_manager.find_user_by_id('100')  # Assuming user ID '100' does not exist in the test data
    assert user is None

# Run the tests
if __name__ == '__main__':
    pytest.main()