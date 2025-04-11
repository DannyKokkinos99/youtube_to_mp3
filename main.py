# import yt_dlp
import yt_dlp as youtube_dl
import eyed3
import os
import re
import subprocess
import discogs_client
from dotenv import load_dotenv
import requests

# Useful website for artwork: https://www.discogs.com/
load_dotenv()


def download_from_playlist(playlist_url):
    command = [
        "yt-dlp",  # The yt-dlp executable
        "-q",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--cookies-from-browser",
        "firefox",  # Path to the cookies file
        "--output",
        f"{ALBUM_FOLDER_PATH}/%(title)s.%(ext)s",
        "--match-filter",
        "duration < 600",
    ]
    command.append(playlist_url)
    print("Downloading files...")
    try:
        subprocess.run(command, check=True)
        print("Download completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during download: {e}")


def clean_mp3_filenames(folder_path):
    patterns = [r"^.* - ", r"\s*\(Audio\)", r" ft\..*?(?=\.mp3$)", r"^.*?：\s*"]

    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        # Only process files ending with .mp3
        if filename.lower().endswith(".mp3"):
            # Create a copy of the filename to modify
            new_filename = filename

            # Apply all regex patterns to remove parts from the filename
            for pattern in patterns:
                new_filename = re.sub(pattern, "", new_filename)

            # Ensure the filename doesn't change if no modification was needed
            if new_filename != filename:
                # Build the full path for renaming
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_filename)

                # Rename the file
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename} ✅")


def set_mp3_metadata_with_cover(folder_path, artist, album, year):
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Only process files ending with .mp3
        if filename.lower().endswith(".mp3"):
            # Construct the full path to the MP3 file
            file_path = os.path.join(folder_path, filename)

            # Load the MP3 file using eyed3
            audio_file = eyed3.load(file_path)

            # Set the title, artist, and album metadata
            title = os.path.splitext(filename)[
                0
            ]  # Use the file name without .mp3 as the title
            audio_file.tag.artist = artist
            audio_file.tag.album = album
            audio_file.tag.title = title
            audio_file.tag.setTextFrame("TDRC", year)

            # Check if cover.jpg exists in the folder and add it as artwork if present
            cover_path = os.path.join(folder_path, "cover.jpg")
            if os.path.exists(cover_path):
                # Open the image file and read it as binary
                with open(cover_path, "rb") as cover_file:
                    cover_data = cover_file.read()
                    # Set the image as album artwork
                    audio_file.tag.images.set(3, cover_data, "image/jpeg")

            # Save the changes to the MP3 file
            audio_file.tag.save()

            print(
                f"Updated metadata for: {filename} -> Title: {title}, Artist: {artist}, Album: {album} ✅"
            )


ARTIST = "Twenty One Pilots"
ALBUM = "Vessel"
YEAR = "2013"

PLAYLIST_URL = (
    "https://www.youtube.com/playlist?list=PLoDAYWBKduzh5L8ISW_etHN0fBdzB_HRg"
)
BASE_FOLDER = "C:/Users/Danny/Music"
ARTIST_FOLDER_PATH = f"{BASE_FOLDER}/{ARTIST}"
ALBUM_FOLDER_PATH = f"{ARTIST_FOLDER_PATH}/{ALBUM}"
OPTIONS = {
    "outtmpl": f"{ALBUM_FOLDER_PATH}/%(title)s.%(ext)s",
    "quiet": True,  # Suppress unnecessary output
    "format": "mp3/bestaudio/best",
    "audio-quality": "0",
    "postprocessors": [
        {  # Extract audio using ffmpeg
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",  # Ensure 320 kbps bitrate
        }
    ],
    "cookies_from_browser": ["firefox"],
}


# Download the songs
# os.makedirs(ARTIST_FOLDER_PATH, exist_ok=True)
# os.makedirs(ALBUM_FOLDER_PATH, exist_ok=True)
# download_from_playlist(PLAYLIST_URL)
# Fix names
# clean_mp3_filenames(ALBUM_FOLDER_PATH)
# Add meta data such as title, album and artist
# set_mp3_metadata_with_cover(ALBUM_FOLDER_PATH, ARTIST, ALBUM, YEAR)


d = discogs_client.Client("my_user_agent/1.0", user_token=os.getenv("DISCO_API"))

# Search for an album
result = d.search("Blurryface", artist="twenty one pilots", type="release")[0]

# Get first result (you can filter further if needed)

title = result.title
year = result.year
thumb = result.thumb  # Small image
cover_image = result.images[0]["uri"] if result.images else "No image available"

print(f"Title: {title}")
print(f"Year: {year}")
print(f"Artwork: {cover_image}")
if cover_image:
    image_response = requests.get(cover_image)

    if image_response.status_code == 200:
        with open(f"cover.jpg", "wb") as file:
            file.write(image_response.content)
    else:
        print(image_response.status_code)
