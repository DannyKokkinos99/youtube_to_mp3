import os
from dotenv import load_dotenv
from utility.logger import get_logger
from flask import Flask, render_template, request, redirect, url_for, flash
from functions import (
    download_mp3,
    set_mp3_metadata_with_cover,
    clean_mp3_filenames,
    get_album_details,
)

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

    BASE_FOLDER = os.getenv(
        "BASE_PATH"
    )  # TODO: Change the base path to a container local address
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

    elif "playlist_urls" in kwargs:
        playlists_folder_path = os.path.join(BASE_FOLDER, "playlists")
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

    elif "song_urls" in kwargs:
        songs_folder_path = os.path.join(BASE_FOLDER, "songs")
        for url in song_urls:
            # # Create folders
            os.makedirs(songs_folder_path, exist_ok=True)
            # # Download the songs
            logger.info(f"Downloading song...")
            download_mp3(songs_folder_path, url)
            logger.info("-> Song downloaded successfully ✅")
    logger.info("Download complete ✅")


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
    form_data = request.form.to_dict()
    logger.debug(form_data)

    if form_data["form_type"] == "album":
        list_albums = form_data["albums"].split(",")
        list_album_urls = form_data["album_urls"].split(",")
        process_submitted_data(
            artist=form_data["artist"],
            albums=list_albums,
            album_urls=list_album_urls,
        )
    elif form_data["form_type"] == "playlists":
        list_playlist_urls = form_data["urls"].split(",")
        process_submitted_data(playlist_urls=list_playlist_urls)
    elif form_data["form_type"] == "songs":
        song_urls = form_data["urls"].split(",")
        process_submitted_data(song_urls=song_urls)
    else:
        print("ISSUE OCCURED DURING DOWNLOADING")
    return redirect(url_for("index"))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)
