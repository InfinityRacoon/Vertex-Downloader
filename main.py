import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YT-Downloader by Infinity")
        self.geometry("600x420")

        # URL Input
        self.url_label = ctk.CTkLabel(self, text="YouTube URL:")
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="w")

        # Format Selection
        self.format_label = ctk.CTkLabel(self, text="Format:")
        self.format_label.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.format_var = ctk.StringVar(value="mp4")
        self.format_mp4 = ctk.CTkRadioButton(self, text="Video (mp4)", variable=self.format_var, value="mp4", command=self.on_format_change)
        self.format_mp4.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="w")
        self.format_mp3 = ctk.CTkRadioButton(self, text="Audio (mp3)", variable=self.format_var, value="mp3", command=self.on_format_change)
        self.format_mp3.grid(row=1, column=1, padx=150, pady=(20, 0), sticky="w")

        # Quality Selection
        self.quality_label = ctk.CTkLabel(self, text="Video Quality:")
        self.quality_label.grid(row=2, column=0, padx=20, pady=(20, 0), sticky="w")
        self.quality_var = ctk.StringVar(value="1080p")
        self.quality_combo = ctk.CTkComboBox(self, values=["720p", "1080p", "2160p"], variable=self.quality_var)
        self.quality_combo.grid(row=2, column=1, padx=20, pady=(20, 0), sticky="w")

        # Path Selection
        self.path_label = ctk.CTkLabel(self, text="Download Path:")
        self.path_label.grid(row=3, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.grid(row=3, column=1, padx=20, pady=(20, 0), sticky="w")
        
        self.path_entry = ctk.CTkEntry(self.path_frame, width=300)
        self.path_entry.grid(row=0, column=0, sticky="w")
        self.path_entry.insert(0, os.path.expanduser("~/Downloads"))
        
        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", width=80, command=self.browse_path)
        self.browse_btn.grid(row=0, column=1, padx=(10, 0), sticky="w")

        # Download Button
        self.download_btn = ctk.CTkButton(self, text="Download", command=self.start_download_thread)
        self.download_btn.grid(row=4, column=0, columnspan=2, padx=20, pady=(40, 20))

        # Progress and Status
        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 20))

    def on_format_change(self):
        if self.format_var.get() == "mp3":
            self.quality_combo.configure(state="disabled")
        else:
            self.quality_combo.configure(state="normal")

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, folder)

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Preparing download...")
        
        thread = threading.Thread(target=self.download)
        thread.daemon = True # ensure thread dies when app closes
        thread.start()

    def my_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                if total_bytes:
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    percentage = downloaded_bytes / total_bytes
                    self.after(0, self.update_progress, percentage, f"Downloading: {percentage*100:.1f}%")
            except Exception:
                pass
        elif d['status'] == 'finished':
            self.after(0, self.update_progress, 1.0, "Processing complete...")

    def update_progress(self, value, text):
        self.progress_bar.set(value)
        self.status_label.configure(text=text)

    def download(self):
        url = self.url_entry.get().strip()
        fmt = self.format_var.get()
        path = self.path_entry.get().strip()
        quality = self.quality_var.get()
        
        try:
            ydl_opts = {
                'outtmpl': f'{path}/%(title)s.%(ext)s',
                'progress_hooks': [self.my_hook],
            }
            
            if fmt == "mp4":
                # height <= resolution string minus the 'p'
                res = quality[:-1]
                ydl_opts['format'] = f'bestvideo[height<={res}]+bestaudio/best[height<={res}]'
                ydl_opts['merge_output_format'] = 'mp4'
            else:
                ydl_opts['format'] = 'bestaudio'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                ydl_opts['ffmpeg_location'] = './'
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            self.after(0, self.download_complete, True, "Download successful!")
        except Exception as e:
            self.after(0, self.download_complete, False, f"Error: {str(e)}")
            
    def download_complete(self, success, message):
        self.status_label.configure(text=message)
        self.download_btn.configure(state="normal")
        if success:
            messagebox.showinfo("Success", "Download completed successfully!")
        else:
            messagebox.showerror("Download Error", message)

if __name__ == "__main__":
    app = App()
    app.mainloop()
