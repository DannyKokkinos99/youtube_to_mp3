import os
from dotenv import load_dotenv
from functions import (
    download_from_playlist,
    set_mp3_metadata_with_cover,
    clean_mp3_filenames,
    get_album_details,
)

# Useful website for artwork: https://www.discogs.com/
load_dotenv()

# Set these variables
ARTIST = "Aurora"
ALBUM = [
    "All My Demons Greeting Me As A Friend",
    "Infections Of A Different Kind (Step 1)",
    "Infections Of A Different Kind (Step 2)",
    "The Gods We Can Touch",
    "What Happened To The Heart",
]
PLAYLIST_URL = [
    "https://www.youtube.com/playlist?list=PLPlCeFqZDUzn4QugqOyyBC1kbJA5VqRvV",
    "https://www.youtube.com/playlist?list=PLfimnwaZdumiIPXflVlv7i3DnepNLnFyW",
    "https://www.youtube.com/playlist?list=PLyq58SwT52VGVTgxnredJzGqJ0gdoZS-O",
    "https://www.youtube.com/playlist?list=PL7QOWfqDaxmD69PYJWrUHJ1TBcma2iz6e",
    "https://www.youtube.com/playlist?list=PLzbGLskt3hhmPtMlmjAIznVe1p8JvBVit",
]
# can edit base folder in .env file
BASE_FOLDER = os.getenv("BASE_PATH")
ARTIST_FOLDER_PATH = os.path.join(BASE_FOLDER, ARTIST)

for album, playlist_url in zip(ALBUM, PLAYLIST_URL):

    album_folder_path = os.path.join(ARTIST_FOLDER_PATH, album)
    # # Create folders
    os.makedirs(ARTIST_FOLDER_PATH, exist_ok=True)
    os.makedirs(album_folder_path, exist_ok=True)
    # # Download the songs
    download_from_playlist(album_folder_path, playlist_url)
    # # Fix names
    clean_mp3_filenames(album_folder_path)
    # # # Get Metadata from disco API
    year = get_album_details(ARTIST, album, album_folder_path)
    if year:
        # Add meta data such as artist and year
        set_mp3_metadata_with_cover(album_folder_path, ARTIST, album, year)
