# Made by Maya!
# Version 2
# Contact me if you need to! EverKitsune6@gmail.com

# Small note! Turns out you can't press share to download the video, you have to copy from addres bar...

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL
import subprocess
import platform
import json
import threading
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                folder = data.get("download_folder")
                if folder and os.path.isdir(folder):
                    return folder
        except Exception:
            pass
    default_folder = os.path.join(BASE_DIR, "Exports")
    os.makedirs(default_folder, exist_ok=True)
    return default_folder

def save_settings(folder):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"download_folder": folder}, f, indent=4)
    except Exception as e:
        print(f"Could not save settings: {e}")

download_folder = load_settings()

def choose_folder():
    global download_folder
    selected = filedialog.askdirectory()
    if selected:
        download_folder = selected
        folder_label.config(text=f"Save Folder: {download_folder}")
        save_settings(download_folder)

def download_video(format_type):
    query = url_entry.get().strip()

    if not query:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL or video title.")
        return

    if query.startswith("http://") or query.startswith("https://"):
        url = query
    else:
        url = f"ytsearch1:{query}"

    mp4_button.config(state=tk.DISABLED)
    mp3_button.config(state=tk.DISABLED)
    ogg_button.config(state=tk.DISABLED)
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, f"Starting {format_type.upper()} download...\n")

    def run_download():
        try:
            output_path = os.path.join(download_folder, '%(title)s.%(ext)s')

            ydl_opts = {
                'quiet': True,
                'noplaylist': True,
                'progress_hooks': [hook],
                'outtmpl': output_path,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                'extractor_args': {
                    'youtube': 'player-client=web_embedded,web,tv'
                },
                'rm_cache_dir': True,
                'verbose': True,
            }

            if format_type == 'mp4':
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'keepvideo': False,
                    'ffmpeg_location': r"C:\Program Files\ffmpeg\bin",
                    'postprocessor_args': ['-loglevel', 'error'],
                    'postprocessors': [{'key': 'FFmpegMerger'}],
                })
            elif format_type == 'section':
                start_time = start_entry.get().strip()
                end_time = end_entry.get().strip()
                if not start_time or not end_time:
                    messagebox.showwarning("Input Error", "Please enter both start and end times in hh:mm:ss format.")
                    return
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'keepvideo': False,
                    'ffmpeg_location': r"C:\Program Files\ffmpeg\bin",
                    'postprocessor_args': [
                        '-ss', start_time, '-to', end_time, '-loglevel', 'error'
                    ],
                    'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
                })
            elif format_type == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif format_type == 'ogg':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'vorbis',
                        'preferredquality': '5',
                    }],
                })
            elif format_type == 'section':
                start_time = start_entry.get().strip()
                end_time = end_entry.get().strip()
                if not start_time or not end_time:
                    messagebox.showwarning("Input Error", "Please enter both start and end times (hh:mm:ss).")
                    return

                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'keepvideo': False,
                    'ffmpeg_location': r"C:\Program Files\ffmpeg\bin",  # adjust if needed
                    'postprocessor_args': [
                        '-ss', start_time, '-to', end_time, '-loglevel', 'error'
                    ],
                    'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
                })


            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                if "WinError 2" not in str(e):
                    log_text.insert(tk.END, f"\n❌ Error: {e}\n")

            log_text.insert(tk.END, f"\n✅ {format_type.upper()} download completed!\n")
            log_text.insert(tk.END, f"Saved to: {download_folder}\n")
        except Exception as e:
            log_text.insert(tk.END, f"\n❌ Error: {e}\n")
        finally:
            mp4_button.config(state=tk.NORMAL)
            mp3_button.config(state=tk.NORMAL)
            ogg_button.config(state=tk.NORMAL)

    threading.Thread(target=run_download).start()

def hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '')
        eta = d.get('_eta_str', '')
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, f"Downloading... {p}\nSpeed: {speed}\nETA: {eta}. Please keep in mind sometimes it says it has an error but it worked fine")
        log_text.see(tk.END)
    elif d['status'] == 'finished':
        log_text.insert(tk.END, "\nDownload finished, finalizing...\n")

def play_recent_file():
    try:
        files = [
            os.path.join(download_folder, f)
            for f in os.listdir(download_folder)
            if f.lower().endswith((".mp3", ".mp4"))
        ]
        if not files:
            messagebox.showinfo("No Files", "No MP3 or MP4 files found in the download folder.")
            return

        recent_file = max(files, key=os.path.getmtime)
        log_text.insert(tk.END, f"\n🎵 Playing: {os.path.basename(recent_file)}\n")

        system = platform.system()
        if system == "Windows":
            os.startfile(recent_file)
        elif system == "Darwin":
            subprocess.call(["open", recent_file])
        else:
            subprocess.call(["xdg-open", recent_file])
    except Exception as e:
        messagebox.showerror("Error", f"Could not play recent file:\n{e}")

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("560x400")
root.resizable(False, False)
root.configure(bg="#E6E6FA")

icon_path = "icon.ico"
image = Image.open("icon.ico")
icon = ImageTk.PhotoImage(image)

tk.Label(root, text="Enter YouTube URL or Video Title:", bg="#E6E6FA").pack(pady=5)
url_entry = tk.Entry(root, width=70)
url_entry.pack(pady=5)

time_frame = tk.Frame(root, bg="#E6E6FA")
time_frame.pack(pady=5)

tk.Label(time_frame, text="Start (hh:mm:ss):", bg="#E6E6FA").pack(side=tk.LEFT, padx=2)
start_entry = tk.Entry(time_frame, width=10)
start_entry.pack(side=tk.LEFT, padx=5)

tk.Label(time_frame, text="End (hh:mm:ss):", bg="#E6E6FA").pack(side=tk.LEFT, padx=2)
end_entry = tk.Entry(time_frame, width=10)
end_entry.pack(side=tk.LEFT, padx=5)

folder_label = tk.Label(root, text=f"Save Folder: {download_folder}", bg="#E6E6FA", fg="gray")
folder_label.pack(pady=5)

frame = tk.Frame(root)
frame.pack(pady=10)
frame.configure(bg="#E6E6FA")

section_button = tk.Button(frame, text="Download Section (MP4)", width=22, command=lambda: download_video('section'))
section_button.pack(side=tk.LEFT, padx=5)

folder_button = tk.Button(root, text="Choose Save Folder", command=choose_folder)
folder_button.pack(pady=5)

mp4_button = tk.Button(frame, text="Download MP4 (Video)", width=18, command=lambda: download_video('mp4'))
mp4_button.pack(side=tk.LEFT, padx=5)

mp3_button = tk.Button(frame, text="Download MP3 (Audio)", width=18, command=lambda: download_video('mp3'))
mp3_button.pack(side=tk.LEFT, padx=5)

ogg_button = tk.Button(frame, text="Download OGG (Audio)", width=18, command=lambda: download_video('ogg'))
ogg_button.pack(side=tk.LEFT, padx=5)

section_button = tk.Button(frame, text="Download Section (MP4)", width=20, command=lambda: download_video('section'))
section_button.pack(side=tk.LEFT, padx=5)

quit_button = tk.Button(root, text="Close", width=10, command=root.destroy)
quit_button.pack(pady=10)

log_text = tk.Text(root, height=10, width=70)
log_text.pack(pady=10)

root.iconphoto(False, icon)
root.mainloop()