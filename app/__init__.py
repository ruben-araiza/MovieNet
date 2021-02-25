from flask import Flask, jsonify

from .imdbscrapper import IMDBScrapper

scrapper = IMDBScrapper()

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/movie/<movie_id>/')
def get_movie_info(movie_id):
    movie_info = scrapper.get_movie_info(movie_id)
    return jsonify(movie_info)


@app.route('/actor/<actor_id>/')
def get_actor_info(actor_id):
    actor_info = scrapper.get_actor_info(actor_id)
    return jsonify(actor_info)
