from flask import Flask, request, jsonify, render_template
import uuid
import requests
import os

app = Flask(__name__)

# Sample data for movies
movies = [
    {"id": "1", "name": "Inception", "year": 2010, "category": "Science Fiction"},
    {"id": "2", "name": "The Shawshank Redemption", "year": 1994, "category": "Drama"},
    {"id": "3", "name": "The Dark Knight", "year": 2008, "category": "Action"},
]

# CRUD Operations

# Get all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    send_event_to_webhook("READ", {"id": ""})
    return jsonify(movies)

# Get a specific movie
@app.route('/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = next((movie for movie in movies if movie['id'] == movie_id), None)
    if movie:
        send_event_to_webhook("READ", {"id": movie_id})
        return jsonify(movie)
    else:
        return jsonify({"error": "Movie not found"}), 404

# Add a new movie
@app.route('/movies', methods=['POST'])
def add_movie():
    data = request.json
    new_movie = {
        "id": str(uuid.uuid4())[:6],
        "name": data['name'],
        "year": data['year'],
        "category": data['category']
    }
    movies.append(new_movie)
    send_event_to_webhook("CREATE", new_movie)
    return jsonify(new_movie), 201

# Edit a movie
@app.route('/movies/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
    movie = next((movie for movie in movies if movie['id'] == movie_id), None)
    if movie:
        data = request.json
        movie.update(data)
        send_event_to_webhook("UPDATE", data)
        return jsonify(movie)
    else:
        return jsonify({"error": "Movie not found"}), 404

# Delete a movie
@app.route('/movies/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    global movies
    movies = [movie for movie in movies if movie['id'] != movie_id]
    send_event_to_webhook("DELETE", {"id": movie_id})
    return '', 204

# Route to serve the HTML interface
@app.route('/')
def index():
    return render_template('index.html', movies=movies)

def send_event_to_webhook(event_type, data):
    # Replace 'webhook_url' with the actual webhook URL
    webhook_url = os.environ.get('WEBHOOK')
    headers = {'Content-Type': 'application/json'}
    payload = {
        'event_type': event_type,
        'data': data
    }
    try:
        response = requests.post(webhook_url, headers=headers, json=payload)
        response.raise_for_status()
        print('Event sent successfully')
        return response.json()
    except requests.exceptions.RequestException as e:
        print('Failed to send event:', e)

if __name__ == '__main__':
    app.run(debug=True)
