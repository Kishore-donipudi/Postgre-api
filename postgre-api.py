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


@app.route('/songs',methods=["GET"]) # getting all songs 
def get_songs():
    try:
        cur.execute("select * from songs")
        songs = cur.fetchall()
        return jsonify(songs), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/songs/<int:id>',methods=["GET"]) #getting songs by id
def get_songs_id(id):
    try:
        cur.execute("select * from songs where id=%s", (id,))
        song = cur.fetchall()
        return jsonify(song), 200
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
        return jsonify(songs), 200
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

@app.route('/artist',methods=["GET"]) #getting all artists
def get_art():
    try:
        cur.execute("select * from artists")
        res = cur.fetchall()
        artists = [{'id': row[0], 'artist': str(row[1]).strip('"'),'img_url':str(row[2]).strip('"')} for row in res]
        return jsonify(artists), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/artist/<int:id>',methods=["GET"]) # getting artist by id
def get_art_id(id):
    try:
        cur.execute("select * from artists where id=%s", (id,))
        artist = cur.fetchall()
        return jsonify([{'id': row[0], 'artist': str(row[1]).strip('"')} for row in artist]), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/artist',methods=["POST"]) # adding new artist
def add_artist():
    try:
        data = request.get_json()
        artist = data.get('artist') or data.get('artist_name')
        if not artist:
            return jsonify({'error': 'Missing required field: artist or artist_name'}), 400
        cur.execute("insert into artists(artist_name) values(%s)", (artist,))
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
        artist = data.get('artist') or data.get('artist_name')
        if not artist:
            return jsonify({'error': 'Missing required field: artist or artist_name'}), 400
        cur.execute(
            "UPDATE artists SET artist_name=%s WHERE id=%s",
            (artist, id)
        )
        conn.commit()
        return jsonify({'message': 'Artist updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    
if __name__=="__main__":

    app.run(debug=True)
