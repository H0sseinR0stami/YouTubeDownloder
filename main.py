import subprocess
import os
import sys
from pathlib import Path


def resource_path(relative_path):
    """Get absolute path to resource, working for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Set paths to bundled executables
YT_DLP_PATH = resource_path("yt-dlp.exe")
FFMPEG_PATH = resource_path("ffmpeg.exe")


def validate_quality_input(max_quality):
    try:
        quality = int(max_quality)
        if quality < 144 or quality > 2160:
            raise ValueError("Quality should be between 144 and 2160")
        return str(quality)
    except ValueError:
        print("⚠️ Invalid quality input. Using default 480p")
        return "480"


def download_video(url, proxy, max_quality="480"):
    print(f"🔽 Downloading (max {max_quality}p)...")

    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)

    # Command with progress reporting
    command = [
        YT_DLP_PATH,
        "--proxy", proxy,
        "--ffmpeg-location", os.path.dirname(FFMPEG_PATH),
        "-f", f"best[height<={max_quality}]",
        "--output", str(download_dir / "%(title)s.%(ext)s"),
        "--newline",  # Enable progress updates in new lines
        "--progress",  # Show progress bar
        "--console-title",  # Update console title with progress
        "--no-continue",
        "--no-part",
        url
    ]

    try:
        # Run with real-time output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Print progress in real-time
        for line in process.stdout:
            # Clean and print progress info
            line = line.strip()
            if line:
                print(line)

        # Wait for process to complete
        process.wait()

        if process.returncode == 0:
            print("✅ Download completed successfully!")
        else:
            print(f"❌ Download failed with exit code {process.returncode}")
            try_fallback_download(url, proxy, max_quality, download_dir)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def try_fallback_download(url, proxy, max_quality, download_dir):
    """Fallback download method with progress reporting"""
    print("⚠️ Trying fallback download method...")
    try:
        command = [
            YT_DLP_PATH,
            "--proxy", proxy,
            "--ffmpeg-location", os.path.dirname(FFMPEG_PATH),
            "-f", f"bestvideo[height<={max_quality}]+bestaudio",
            "--merge-output-format", "mp4",
            "--output", str(download_dir / "%(title)s.%(ext)s"),
            "--newline",
            "--progress",
            "--console-title",
            url
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        for line in process.stdout:
            line = line.strip()
            if line:
                print(line)

        process.wait()

        if process.returncode == 0:
            print("✅ Download completed using fallback method!")
        else:
            print(f"❌ Fallback download failed with exit code {process.returncode}")

    except Exception as e:
        print(f"❌ Error in fallback download: {e}")


if __name__ == "__main__":
    url = input("🎬 Enter the YouTube video URL: ").strip()
    if not url:
        print("⚠️ URL is required.")
        sys.exit(1)

    max_quality = input("📺 Enter maximum quality (default 480): ").strip()
    max_quality = validate_quality_input(max_quality) if max_quality else "480"

    proxy = "socks5://127.0.0.1:10808"
    download_video(url, proxy, max_quality)