import eyed3
import os
import re
import subprocess
import discogs_client
import requests


def download_from_playlist(album_path, playlist_url):
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
        f"{album_path}/%(title)s.%(ext)s",
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
    patterns = [
        r"^.* - ",
        r"\s*\(Audio\)",
        r"\s*ft\..*?(?=\.\w+$)",
        r"\s*feat\..*?(?=\.\w+$)",
        r"\s*\([^)]*\)",
        r"\s*\[[^]]*\]",
    ]

    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        # Only process files ending with .mp3
        if filename.lower().endswith(".mp3"):
            # Create a copy of the filename to modify
            new_filename = filename

            # Apply all regex patterns to remove parts from the filename
            for pattern in patterns:
                new_filename = re.sub(pattern, "", new_filename)
            # Skip names that are contained within a bracket
            if new_filename == ".mp3":
                continue

            if new_filename != filename:
                # Build the full path for renaming
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_filename)

                try:
                    os.rename(old_path, new_path)
                except FileExistsError:
                    print(f"Failed to rename {filename} as name already exists❌")
                    continue

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


def get_album_details(artist, album, album_path):

    token = os.getenv("DISCO_TOKEN")
    user_agent = "my_user_agent/1.0"
    d = discogs_client.Client(user_agent, user_token=token)
    # # Search for an album
    try:
        result = d.search(album, artist=artist, type="release")[0]
    except IndexError:
        print(f"No release found for '{album}' by '{artist}' ❌")
        return None
    year = result.year
    images = result.images
    cover_image_url = images[0]["uri"] if images else None

    if cover_image_url:
        try:
            headers = {"User-Agent": user_agent}
            response = requests.get(cover_image_url, stream=True, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Determine the filename from the URL
            filename = os.path.join(album_path, "cover.jpg")

            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Artwork downloaded to: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading artwork: {e}")
            return None
    else:
        print("No artwork available for this release.")
        return None
    return year
