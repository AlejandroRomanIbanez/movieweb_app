from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView



db = SQLAlchemy()

user_movie_association = db.Table(
    'user_movie_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id'))
)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    movies = db.relationship('Movie', secondary=user_movie_association, back_populates='users')
    profile_picture = db.Column(db.String, nullable=True, default='images/default_profile.jpg')

    def __repr__(self):
        return f"<User id={self.user_id}, name='{self.name}', password={self.password}>"

    def __str__(self):
        return f"Author: {self.name}"

    def get_id(self):
        # Return the user's user_id as a string
        return str(self.user_id)


class Movie(db.Model):
    __tablename__ = 'movie'
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    director = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.String, nullable=True)
    poster = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    users = db.relationship('User', secondary=user_movie_association, back_populates='movies')

    def __repr__(self):
        return f"<Movie id={self.movie_id}, title='{self.title}', director='{self.director}', year={self.year}, rating={self.rating}>"

    def __str__(self):
        return f"Movie: {self.title}"

class Review(db.Model):
    __tablename__ = 'review'
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), nullable=False)
    review_text = db.Column(db.String, nullable=False)
    user_rating = db.Column(db.Float, nullable=False)
    user = db.relationship('User')
    movie = db.relationship('Movie')
    def __repr__(self):
        return f"<Review id={self.review_id}, user_id={self.user_id}, movie_id={self.movie_id}, user_rating={self.user_rating}>"

    def __str__(self):
        return f"Review by User {self.user_id} for Movie {self.movie_id} with rating {self.user_rating}"

class MovieView(ModelView):
    form_columns = ["title", "users"]

class ReviewView(ModelView):
    form_columns = ["user"]

class UserView(ModelView):
    column_list = ['user_id', 'name', 'password', 'profile_picture']
    column_filters = ['name']
    column_searchable_list = ['name']



def print_all_data():
    all_users = User.query.all()
    all_movies = Movie.query.all()
    all_reviews = Review.query.all()

    print("All Users:")
    for user in all_users:
        print(f"{user.user_id} --> {user.name} --> {user.password} --> {user.movies}")

    print("\nAll Movies:")
    for movie in all_movies:
        print(f" {movie.movie_id} --> {movie.title} --> {movie.director} --> {movie.year} --> {movie.rating} --> {movie.poster} --> {movie.users}")

    print("\nAll Reviews:")
    for review in all_reviews:
        print(
            f" {review.review_id} --> User: {review.user_id} --> Movie: {review.movie_id} --> Rating: {review.user_rating} --> {review.review_text}")

