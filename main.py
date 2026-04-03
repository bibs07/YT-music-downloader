import yt_dlp
import os
import sys
from downloader_lib import process_song

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    print("\n--- YT Music Downloader (Guest Mode) ---")
    user_url = input("Paste Song or Playlist URL: ").strip()

    is_playlist = "list=" in user_url and "watch?v=" not in user_url
    links_to_download = []

    extract_opts = {
        'extract_flat': True, 
        'quiet': True, 
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'skip': ['dash', 'hls']
            }
        },
    }

    with yt_dlp.YoutubeDL(extract_opts) as ydl:
        print("🔍 Scanning (Guest Mode)...")
        try:
            info = ydl.extract_info(user_url, download=False)
            if is_playlist and 'entries' in info:
                print(f"Found Playlist: {info.get('title', 'Unknown')}")
                for entry in info['entries']:
                    url = entry.get('url') or entry.get('webpage_url')
                    if url: links_to_download.append(url.replace("/shorts/", "/watch?v="))
            else:
                links_to_download.append(user_url.replace("/shorts/", "/watch?v="))
        except Exception as e:
            print(f"❌ Access Error: {e}")
            return

    total_songs = len(links_to_download)
    if total_songs == 0: return

    print(f"\nTargeting {total_songs} song(s).")
    confirm = input(f"Proceed with batch? (y/n): ").lower().strip()

    if confirm == 'y':
        try:
            for i, url in enumerate(links_to_download, 1):
                print(f"[{i}/{total_songs}]", end=" ", flush=True)
                try:
                    process_song(url)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"⚠️ Error on track {i}: {e}")
            print("\n🎉 All tasks completed!")
        except KeyboardInterrupt:
            print("\n\n🛑 User interrupted. Shutting down...")
            sys.exit(0)
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()