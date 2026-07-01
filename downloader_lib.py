import yt_dlp
from mutagen.id3 import ID3, APIC, TIT2, TPE1
from PIL import Image
import os
import glob
import io
import re

# Custom silent logger to swallow all internal yt-dlp chatter
class SilentLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def sanitize(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_expected_filename(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(artist)s - %(title)s.%(ext)s',
        'quiet': True, 
        'no_warnings': True,
        'logger': SilentLogger(),
        'skip_download': True, 
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android'],
                'skip': ['dash', 'hls']
            }
        },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info: return None
            
            # Use yt-dlp's internal naming parsing
            fake_filepath = ydl.prepare_filename(info)
            base_path = os.path.splitext(fake_filepath)[0]
            folder, filename = os.path.split(base_path)
            
            return os.path.join(folder, f"{sanitize(filename)}.mp3")
        except: 
            return None

def process_song(url):
    expected_mp3_path = get_expected_filename(url)
    if expected_mp3_path and os.path.exists(expected_mp3_path):
        print(f"⏭️  SKIPPING: '{os.path.basename(expected_mp3_path)}'")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(artist)s - %(title)s.%(ext)s',
        'writethumbnail': True,
        'quiet': True,
        'no_warnings': True,
        'logger': SilentLogger(),
        'nocheckcertificate': True,
        'allow_remote_components': True,
        'js_runtimes': {'node': {}},
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android'],
                'skip': ['dash', 'hls']
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info: return

            original_filepath = ydl.prepare_filename(info)
            base_path = os.path.splitext(original_filepath)[0]
            expected_mp3 = f"{base_path}.mp3"
            
            folder, filename = os.path.split(base_path)
            final_mp3_path = os.path.join(folder, f"{sanitize(filename)}.mp3")

            if os.path.exists(expected_mp3):
                os.rename(expected_mp3, final_mp3_path)
            else: return

            audio = ID3(final_mp3_path)
            art_files = glob.glob(f"{base_path}.*")
            for img_path in art_files:
                if img_path.lower().endswith(('.webp', '.jpg', '.jpeg', '.png')):
                    try:
                        with Image.open(img_path) as img:
                            img = img.convert("RGB")
                            buf = io.BytesIO()
                            img.save(buf, format='JPEG', quality=90)
                            audio.add(APIC(3, 'image/jpeg', 3, 'Cover', buf.getvalue()))
                        os.remove(img_path)
                    except: pass
                    break

            audio.add(TIT2(encoding=3, text=info.get('title', 'Unknown')))
            audio.add(TPE1(encoding=3, text=info.get('artist') or info.get('uploader', 'Unknown')))
            audio.save(final_mp3_path, v2_version=3)
            print(f"✅ DONE: {os.path.basename(final_mp3_path)}")

    except Exception as e:
        print(f"🚫 FAILED: {url} | Reason: {str(e)[:100]}")