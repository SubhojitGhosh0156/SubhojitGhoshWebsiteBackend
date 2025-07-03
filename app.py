import os
import json
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATA_FILE = 'data.json'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper functions to read/write JSON

def read_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# API Endpoints

@app.route('/posts', methods=['GET'])
def get_posts():
    data = read_data()
    return jsonify(data['posts'])

@app.route('/posts', methods=['POST'])
def add_post():
    data = read_data()
    text = request.form.get('text')
    image = None
    video = None
    if 'image' in request.files and request.files['image'].filename:
        img = request.files['image']
        ext = os.path.splitext(img.filename or '')[1] or '.jpg'
        filename = f"image_{uuid.uuid4().hex}{ext}"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(image_path)
        image = image_path
    if 'video' in request.files and request.files['video'].filename:
        vid = request.files['video']
        ext = os.path.splitext(vid.filename or '')[1] or '.mp4'
        filename = f"video_{uuid.uuid4().hex}{ext}"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        vid.save(video_path)
        video = video_path
    post_id = max([p['id'] for p in data['posts']] + [0]) + 1
    post = {
        'id': post_id,
        'text': text,
        'image': image,
        'video': video,
        'comments': []
    }
    data['posts'].append(post)
    write_data(data)
    return jsonify(post), 201

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    data = read_data()
    post_to_delete = None
    for post in data['posts']:
        if post['id'] == post_id:
            post_to_delete = post
            break
    if post_to_delete:
        # Optionally delete the file from uploads
        if post_to_delete.get('image') and os.path.exists(post_to_delete['image']):
            os.remove(post_to_delete['image'])
        if post_to_delete.get('video') and os.path.exists(post_to_delete['video']):
            os.remove(post_to_delete['video'])
        data['posts'] = [p for p in data['posts'] if p['id'] != post_id]
        write_data(data)
        return '', 204
    return jsonify({'error': 'Post not found'}), 404

@app.route('/comments/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    data = read_data()
    comment = request.json.get('comment') if request.json else None
    for post in data['posts']:
        if post['id'] == post_id:
            post['comments'].append(comment)
            break
    write_data(data)
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = read_data()
    password = request.json.get('password') if request.json else None
    return jsonify({'success': password == data['password']})

@app.route('/change-password', methods=['POST'])
def change_password():
    data = read_data()
    old = request.json.get('old_password') if request.json else None
    new = request.json.get('new_password') if request.json else None
    if old == data['password']:
        data['password'] = new
        write_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Incorrect password'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Create data.json if it doesn't exist
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({'password': 'Subhojitghosh30102000#', 'posts': []}, f)
    app.run(debug=True) 