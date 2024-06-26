from flask import Flask, request, jsonify, render_template
import uuid
import requests
import os

app = Flask(__name__)

# CRUD Operations

# Get all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        response = send_event_to_webhook("READ", {"id": ""})
        if response.ok:
            return jsonify(response.json()[0])
        else:
            return jsonify({"error": "Failed to fetch movies"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# Get a specific movie
@app.route('/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    try:
        response = send_event_to_webhook("READ", {"id": movie_id})
        return jsonify(response.json())
    except:
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

    send_event_to_webhook("CREATE", new_movie)
    return new_movie, 201

# Edit a movie
@app.route('/movies/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Ensure the movie ID in the URL is the one being updated
        data['id'] = movie_id

        response = send_event_to_webhook("UPDATE", data)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to update movie"}), response.status_code

    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
# Delete a movie
@app.route('/movies/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    send_event_to_webhook("DELETE", {"id": movie_id})
    return '', 204

# Route to serve the HTML interface
@app.route('/')
def index():
    return render_template('index.html')

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
        print('Response from webhook:', response.json()) 
        return response
    except requests.exceptions.RequestException as e:
        print('Failed to send event:', e)

if __name__ == '__main__':
    app.run(debug=True)
