import os
import re
import streamlit as st
import imageio_ffmpeg
from yt_dlp import YoutubeDL

# Set FFmpeg path
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["FFMPEG_BINARY"] = ffmpeg_path

def sanitize_filename(title):
    """Remove invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', "_", title)

def search_youtube(query):
    """Search YouTube and return the first video URL."""
    search_query = f"ytsearch5:{query}"
    search_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    
    with YoutubeDL(search_opts) as ydl:
        try:
            result = ydl.extract_info(search_query, download=False)
            if result and 'entries' in result and len(result['entries']) > 0:
                first_entry = result['entries'][0]
                video_url = first_entry.get('url')
                video_title = first_entry.get('title')
                return video_url, video_title
        except Exception as e:
            st.error(f"Error while searching: {e}")
    
    return None, None

def download_audio(video_url, song_title):
    """Download the audio from a YouTube video URL as MP3."""
    safe_title = sanitize_filename(song_title)  # Sanitize file name
    ydl_opts = {
        'format': 'bestaudio/best',
        'extract_audio': True,
        'audio_format': 'mp3',
        'outtmpl': f'{safe_title}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            return f"{safe_title}.mp3"
        except Exception as e:
            st.error(f"Error while downloading: {e}")
            return None

def download_video(video_url, video_title):
    """Download the video from a YouTube video URL as MP4."""
    safe_title = sanitize_filename(video_title)  # Sanitize file name
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{safe_title}.%(ext)s',
        'ffmpeg_location': ffmpeg_path
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            return f"{safe_title}.mp4"
        except Exception as e:
            st.error(f"Error while downloading: {e}")
            return None


# Streamlit UI
st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("🎶 YouTube Video & Audio Downloader 🎥")

song_name = st.text_input("Enter song name or video title:")

download_type = st.radio("Choose download type:", ["Audio (MP3)", "Video (MP4)"])

if st.button("Search & Download"):
    if song_name:
        video_url, video_title = search_youtube(song_name)
        
        if video_url:
            st.success(f"Found: {video_title}")
            st.write(f"Downloading from: {video_url}")

            if download_type == "Audio (MP3)":
                file_path = download_audio(video_url, video_title)
            else:
                file_path = download_video(video_url, video_title)

            if file_path:
                st.success(f"Download complete! Saved as {file_path}")
        else:
            st.error("No results found. Try a different search term.")
    else:
        st.warning("Please enter a song or video title.")
