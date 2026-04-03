import yt_dlp
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC
from PIL import Image
import os
import glob
import io
import re

def sanitize(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_expected_filename(url):
    ydl_opts = {
        'quiet': True, 
        'skip_download': True, 
        'nocheckcertificate': True,
        'extractor_args': {'youtube': {'player_client': ['android']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info: return None
            artist = info.get('artist') or info.get('uploader', 'Unknown')
            title = info.get('title', 'Unknown')
            return f"{sanitize(f'{artist} - {title}')}.mp3"
        except: return None

def process_song(url):
    expected_name = get_expected_filename(url)
    if expected_name and os.path.exists(os.path.join('downloads', expected_name)):
        print(f"⏭️  SKIPPING: '{expected_name}'")
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