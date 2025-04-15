import os
import random
import string
from dotenv import load_dotenv
from utility.logger import get_logger
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from functions import (
    download_mp3,
    set_mp3_metadata_with_cover,
    clean_mp3_filenames,
    get_album_details,
    serve_content,
    delete_local_content,
)

BASE_FOLDER = "music"
load_dotenv()
logger = get_logger(__name__)
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")


# --- This is the function where your submitted data will go ---
def process_submitted_data(**kwargs):
    artist = kwargs.get("artist")
    albums = kwargs.get("albums")
    album_urls = kwargs.get("album_urls")
    playlist_urls = kwargs.get("playlist_urls")
    song_urls = kwargs.get("song_urls")

    os.makedirs(BASE_FOLDER, exist_ok=True)
    if "album_urls" in kwargs:
        ARTIST_FOLDER_PATH = os.path.join(BASE_FOLDER, artist)
        for album, url in zip(albums, album_urls):
            album_folder_path = os.path.join(ARTIST_FOLDER_PATH, album)
            # # Create folders
            os.makedirs(ARTIST_FOLDER_PATH, exist_ok=True)
            os.makedirs(album_folder_path, exist_ok=True)
            # # Download the songs
            logger.info(f"Downloading album {album}...")
            download_mp3(album_folder_path, url)
            # # Fix names
            logger.info(f"-> Steralising files:")
            clean_mp3_filenames(album_folder_path)
            # # # Get Metadata from disco API
            year = get_album_details(artist, album, album_folder_path)
            if year:
                # Add meta data such as artist and year
                logger.info(f"-> Adding metadata:")
                set_mp3_metadata_with_cover(album_folder_path, artist, album, year)
            logger.info("-> Album downloaded successfully ✅\n\n")
        zip_filename = serve_content(BASE_FOLDER, artist)

    elif "playlist_urls" in kwargs:
        random_chars = "".join(
            random.choices(string.ascii_letters + string.digits, k=4)
        )
        playlist_folder = f"playlists-{random_chars}"
        playlists_folder_path = os.path.join(BASE_FOLDER, playlist_folder)
        for i, url in enumerate(playlist_urls):
            playlist_folder_path = os.path.join(
                playlists_folder_path, f"playlist-{i+1}"
            )
            # # Create folders
            os.makedirs(playlists_folder_path, exist_ok=True)
            os.makedirs(playlist_folder_path, exist_ok=True)
            # # Download the songs
            logger.info(f"Downloading playlist-{i}...")
            download_mp3(playlist_folder_path, url)
            logger.info("-> Playlist downloaded successfully ✅")
        zip_filename = serve_content(BASE_FOLDER, playlist_folder)

    elif "song_urls" in kwargs:
        main_folder_name = "songs"
        songs_folder_path = os.path.join(BASE_FOLDER, main_folder_name)
        for url in song_urls:
            # # Create folders
            os.makedirs(songs_folder_path, exist_ok=True)
            # # Download the songs
            logger.info(f"Downloading song...")
            download_mp3(songs_folder_path, url)
            logger.info("-> Song downloaded successfully ✅")
        zip_filename = serve_content(BASE_FOLDER, main_folder_name)
    logger.info("Download complete ✅")

    return zip_filename


# --- Flask Routes ---
@app.route("/get-form", methods=["GET"])
def get_form():
    form_type = request.args.get("form")
    if form_type == "albums":
        return render_template("album_form.html")
    elif form_type == "playlists":
        return render_template("playlist_form.html")
    elif form_type == "song":
        return render_template("song_form.html")
    elif form_type == "":
        return render_template("default.html")


@app.route("/download", methods=["POST"])
def prepare_content():
    delete_local_content(BASE_FOLDER)
    form_data = request.form.to_dict()
    # logger.debug(form_data)

    if form_data["form_type"] == "album":
        list_albums = form_data["albums"].split(",")
        list_album_urls = form_data["album_urls"].split(",")
        zip_filename = process_submitted_data(
            artist=form_data["artist"],
            albums=list_albums,
            album_urls=list_album_urls,
        )
        return send_file(zip_filename, as_attachment=True)
    elif form_data["form_type"] == "playlists":
        list_playlist_urls = form_data["urls"].split(",")
        zip_filename = process_submitted_data(playlist_urls=list_playlist_urls)
        return send_file(zip_filename, as_attachment=True)
    elif form_data["form_type"] == "songs":
        song_urls = form_data["urls"].split(",")
        zip_filename = process_submitted_data(song_urls=song_urls)
        return send_file(zip_filename, as_attachment=True)
    else:
        print("ISSUE OCCURED DURING DOWNLOADING")
    return redirect(url_for("index"))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# --- Run the App ---
if __name__ == "__main__":
    app.run(port=5005, host="0.0.0.0")
