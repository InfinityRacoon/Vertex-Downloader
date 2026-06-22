import yt_dlp
import sys
print("YT-Downloader created by Infinity")
link =input("Enter YouTube video link: ")
type =input("Enter video type (mp4 = 1, mp3 = 2): ")
type_map = {
    "1": "mp4",
    "2": "mp3"
}
actual_type = type_map.get(type, "Unknown Value. Reset program?")
path =input("Enter download path: ")
if type == "1":
    quality = input("Enter video quality (720p = 1, 1080p HD = 2, 4K = 3): ")
    quality_map = {
        "1": "720p",
        "2": "1080p",
        "3": "2160p"
    }
    actual_quality = quality_map.get(quality, "Unknown Value. Reset program?")
    output = input("The following media metadata will be generated: Link: " + link + ", Format: " + actual_type + ", Quality: " + actual_quality + ", Path: " + path + "\n Confirm? (y/n): ")
    if output=="y":
        with yt_dlp.YoutubeDL({
            'format': f'bestvideo[height<={actual_quality[:-1]}]+bestaudio/best[height<={actual_quality[:-1]}]',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4'
        }) as ydl:
            ydl.download([link])
    else:
        print("Download cancelled. Reset the program to retry.")
        sys.exit()
elif type == "2":
    output = input("The following media metadata will be generated: Link: " + link + ", Format: " + actual_type + ", Path: " + path + "\n Confirm? (y/n): ")
    if output=="y":
        with yt_dlp.YoutubeDL({
            'format': 'bestaudio',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': './'
        }) as ydl:
            ydl.download([link])
            print("Download completed.")
    else:
        print("Download cancelled. Reset the program to retry.")
        sys.exit()
else:
    print("An error occurred. Reset the program. ")
    sys.exit()