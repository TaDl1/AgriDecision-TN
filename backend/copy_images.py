import shutil
import os

source_dir = r"C:\Users\asus\.gemini\antigravity\brain\c3589325-74a7-4f6a-b33c-8d815d413444"
dest_dir = r"d:\AgriDecision-TN\frontend\public\images\crops"

files_to_copy = [
    ("uploaded_image_0_1767728549950.jpg", "fava_beans.jpg"),
    ("uploaded_image_1_1767728549950.jpg", "green_peas.jpg"),
    ("uploaded_image_2_1767728549950.png", "melon.png")
]

def copy_images():
    if not os.path.exists(dest_dir):
        print(f"Destination directory does not exist: {dest_dir}")
        return

    for src_name, dest_name in files_to_copy:
        src_path = os.path.join(source_dir, src_name)
        dest_path = os.path.join(dest_dir, dest_name)
        
        try:
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)
                print(f"Success: Copied {src_name} to {dest_name}")
            else:
                print(f"Error: Source file not found: {src_path}")
        except Exception as e:
            print(f"Error copying {src_name}: {e}")

if __name__ == "__main__":
    copy_images()
