"""
TeleRAG 2.0 - Model Downloader
Downloads the official Qwen 2.5 3B Instruct 4-bit GGUF model from Hugging Face.
Source: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf
"""
import os
import sys
import urllib.request

MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
DEST_FILE = os.path.join(DEST_DIR, "qwen2.5-3b-instruct-q4_k_m.gguf")


def download_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100.0, downloaded * 100.0 / total_size)
        mb_down = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        sys.stdout.write(f"\r[TeleRAG] Downloading Qwen 2.5 3B: {percent:5.1f}% [{mb_down:6.1f} MB / {mb_total:6.1f} MB]")
        sys.stdout.flush()


def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    if os.path.exists(DEST_FILE):
        size_mb = os.path.getsize(DEST_FILE) / (1024 * 1024)
        print(f"[TeleRAG] Model already exists at: {DEST_FILE} ({size_mb:.1f} MB)")
        print("[TeleRAG] Ready to run with full neural GPU acceleration!")
        return

    print(f"[TeleRAG] Downloading Qwen 2.5 3B Instruct (4-bit GGUF, ~2.10 GB)...")
    print(f"Source: {MODEL_URL}")
    print(f"Target: {DEST_FILE}\n")
    try:
        urllib.request.urlretrieve(MODEL_URL, DEST_FILE, reporthook=download_progress)
        print("\n\n[TeleRAG] SUCCESS: Model downloaded and ready for local inference.")
    except Exception as e:
        print(f"\n\n[TeleRAG] Download error: {e}")
        print("[TeleRAG] You can manually download the file from:")
        print(f"  {MODEL_URL}")
        print(f"and place it inside the 'models/' folder as: {DEST_FILE}")


if __name__ == "__main__":
    main()
