
import psycopg2
from flask import Flask,request,jsonify
from flask_cors import CORS
import os 
from dotenv import load_dotenv
load_dotenv()
db_url=os.getenv("DATABSE_URL")
conn=psycopg2.connect(db_url)

app=Flask(__name__)
CORS(app)

cur=conn.cursor()



# Helper to get column names for songs table
@app.route('/',methods=["GET"])
def get_song_columns():
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'songs'")
    return [row[0] for row in cur.fetchall()]

@app.route('/songs',methods=["GET"]) # getting all songs 
def get_songs():
    try:
        cur.execute("select * from songs")
        songs = cur.fetchall()
        # Map DB columns to custom keys for frontend
        songs_list = [
            {
                'song_id': row[0],
                'song_name': row[1],
                'url': row[2],
                'type': row[3],
                'artist_id': row[4]
            }
            for row in songs
        ]
        return jsonify(songs_list), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/songs/<int:id>',methods=["GET"]) #getting songs by id
def get_songs_id(id):
    try:
        cur.execute("select * from songs where id=%s", (id,))
        song = cur.fetchall()
        song_list = [
            {
                'song_id': row[0],
                'song_name': row[1],
                'url': row[2],
                'type': row[3],
                'artist_id': row[4]
            }
            for row in song
        ]
        return jsonify(song_list), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/songs/search',methods=["GET"]) # searching songs by title
def search_songs():
    try:
        q = request.args.get('filename') or request.args.get('q')
        if not q:
            return jsonify({'error': 'Missing search query parameter'}), 400
        cur.execute("select * from songs where filename like %s", ('%' + q + '%',))
        songs = cur.fetchall()
        songs_list = [
            {
                'song_id': row[0],
                'song_name': row[1],
                'url': row[2],
                'type': row[3],
                'artist_id': row[4]
            }
            for row in songs
        ]
        return jsonify(songs_list), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/songs',methods=["POST"]) # adding new song
def add_song():
    try:
        data = request.get_json()
        if not ("select * from Artsits where id=%s", (data['artist_id'],)):
            return jsonify({'error': 'Artist ID does not exist'}), 400
        if not all(k in data for k in ("filename", "url", "type", "artist_id")):
            return jsonify({'error': 'Missing required fields'}), 400
        cur.execute("insert into songs(filename,url,type,artist_id) values(%s,%s,%s,%s)", (data['filename'], data['url'], data['type'], data['artist_id']))
        conn.commit()
        return jsonify({'message': 'Song added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

# PATCH and DELETE for songs
@app.route('/songs/<int:id>', methods=["PATCH"])
def patch_song(id):
    try:
        data = request.get_json()
        fields = []
        values = []
        for key, db_col in {
            'song_name': 'filename',
            'url': 'url',
            'type': 'type',
            'artist_id': 'artist_id'
        }.items():
            if key in data:
                fields.append(f"{db_col}=%s")
                values.append(data[key])
        if not fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        values.append(id)
        cur.execute(f"UPDATE songs SET {', '.join(fields)} WHERE id=%s", tuple(values))
        conn.commit()
        return jsonify({'message': 'Song updated (patch) successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/songs/<int:id>', methods=["DELETE"])
def delete_song(id):
    try:
        cur.execute("DELETE FROM songs WHERE id=%s", (id,))
        conn.commit()
        return jsonify({'message': 'Song deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

# PATCH and DELETE for artists
@app.route('/artist/<int:id>', methods=["PATCH"])
def patch_artist(id):
    try:
        data = request.get_json()
        fields = []
        values = []
        for key, db_col in {
            'name': 'artist_name',
            'img': 'img_url'
        }.items():
            if key in data:
                fields.append(f"{db_col}=%s")
                values.append(data[key])
        if not fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        values.append(id)
        cur.execute(f"UPDATE artists SET {', '.join(fields)} WHERE id=%s", tuple(values))
        conn.commit()
        return jsonify({'message': 'Artist updated (patch) successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/artist/<int:id>', methods=["DELETE"])
def delete_artist(id):
    try:
        cur.execute("DELETE FROM artists WHERE id=%s", (id,))
        conn.commit()
        return jsonify({'message': 'Artist deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
@app.route('/artist',methods=["GET"]) #getting all artists
def get_art():
    try:
        cur.execute("select * from artists")
        res = cur.fetchall()
        artists = [
            {
                'id': row[0],
                'name': row[1],
                'img': row[2]
            }
            for row in res
        ]
        return jsonify(artists), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/artist/<int:id>',methods=["GET"]) # getting artist by id
def get_art_id(id):
    try:
        cur.execute("select * from artists where id=%s", (id,))
        artist = cur.fetchall()
        artist_list = [
            {
                'id': row[0],
                'name': row[1],
                'img': row[2]
            }
            for row in artist
        ]
        return jsonify(artist_list), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/artist',methods=["POST"]) # adding new artist
def add_artist():
    try:
        data = request.get_json()
        name = data.get('name') or data.get('artist') or data.get('artist_name')
        img = data.get('img') or data.get('img_url')
        if not name:
            return jsonify({'error': 'Missing required field: name/artist/artist_name'}), 400
        cur.execute("insert into artists(artist_name, img_url) values(%s, %s)", (name, img))
        conn.commit()
        return jsonify({'message': 'Artist added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

# Update song by id
@app.route('/songs/<int:id>', methods=["PUT"])
def update_song(id):
    try:
        data = request.get_json()
        fields = ["filename", "url", "type", "artist_id"]
        if not all(k in data for k in fields):
            return jsonify({'error': 'Missing required fields'}), 400
        cur.execute(
            "UPDATE songs SET filename=%s, url=%s, type=%s, artist_id=%s WHERE id=%s",
            (data["filename"], data["url"], data["type"], data["artist_id"], id)
        )
        conn.commit()
        return jsonify({'message': 'Song updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

# Update artist by id
@app.route('/artist/<int:id>', methods=["PUT"])
def update_artist(id):
    try:
        data = request.get_json()
        name = data.get('name') or data.get('artist') or data.get('artist_name')
        img = data.get('img') or data.get('img_url')
        if not name:
            return jsonify({'error': 'Missing required field: name/artist/artist_name'}), 400
        cur.execute(
            "UPDATE artists SET artist_name=%s, img_url=%s WHERE id=%s",
            (name, img, id)
        )
        conn.commit()
        return jsonify({'message': 'Artist updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    
if __name__=="__main__":
    app.run(debug=True)
