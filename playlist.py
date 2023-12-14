import os
import shutil
import argparse
import unicodedata
from tqdm import tqdm

def read_m3u_playlist(file_path):
    with open(file_path, 'r') as file:
        
        return [line.strip() for line in file]

def sanitize_name(name):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '：', '・','　']
    new_name = name.rstrip('.').replace('...', '..')

    for char in invalid_chars:
        new_name = new_name.replace(char, '_')
    new_name = unicodedata.normalize('NFC', new_name)

    return new_name

def unique_name(destination, original_name):
    base, ext = os.path.splitext(original_name)
    counter = 1
    new_name = original_name
    while os.path.exists(os.path.join(destination, new_name)):
        new_name = f"{base}_{counter}{ext}"
        counter += 1
    return new_name

def copy_music_files(file_paths, src_base_path, dest_base_path, sdcard_path):
    for file_path in tqdm(file_paths, desc="Copying files"):
        if not file_path.startswith('#'):  # Only process non-comment lines
            file_path = file_path[3:]
            src = os.path.join(src_base_path, file_path)
            if os.path.exists(src):
                dest = os.path.join(dest_base_path, file_path)
                

                # Sanitize folder and file names
                dest_parts = dest.split(os.sep)
                dest_sanitized = os.sep.join([sanitize_name(part) for part in dest_parts])

                dest_folder = os.path.dirname(dest_sanitized)

                # Check if dest_folder is under sdcard_path
                if not dest_folder.startswith(sdcard_path):
                    raise ValueError("Destination folder is not under sdcard_path")

                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)

                if not os.path.exists(dest_sanitized):
                    shutil.copy2(src, dest_sanitized)
                    tqdm.write(f"Copied: {src} to {dest_sanitized}")
                # else:
                    # print(f"Skipped: (already exists): {dest}")

                # # Handle duplicate names after sanitization
                # if dest != dest_sanitized:
                #     dest_sanitized_folder = os.path.dirname(dest_sanitized)
                #     # dest_sanitized = os.path.join(dest_sanitized_folder, unique_name(dest_folder, os.path.basename(dest_sanitized)))
                #     if not os.path.exists(dest_sanitized_folder):
                #         os.makedirs(dest_sanitized_folder)

                #     shutil.move(dest, dest_sanitized)
                #     print(f"Renamed: {dest} to {dest_sanitized}")


def create_new_playlist(original_playlist_path, new_playlist_path, src_base_path, dest_base_path):
    file_paths = read_m3u_playlist(original_playlist_path)
    with open(new_playlist_path, 'w') as new_playlist:
        for file_path in tqdm(file_paths, desc=f"Creating {os.path.basename(new_playlist_path)}"):
            if not file_path.startswith('#'):  # Only process non-comment lines
                file_path = file_path[3:]
                new_path = os.path.join(dest_base_path, file_path)
                new_path_sanitized = os.sep.join([sanitize_name(part) for part in new_path.split(os.sep)])

                final_path = os.path.join(dest_base_path, new_path_sanitized)

                # if new_path != new_path_sanitized:
                #     final_path = os.path.join(dest_base_path, unique_name(dest_base_path, new_path_sanitized))

                new_path_relative = os.path.relpath(final_path, start=os.path.dirname(new_playlist_path))
                new_playlist.write(new_path_relative + '\n')

def main():
    parser = argparse.ArgumentParser(description='Copy music files and create playlists.')
    parser.add_argument('playlist_name', nargs='+', help='Name of the playlist file(s) (with or without .m3u extension)')

    args = parser.parse_args()
    playlist_names = args.playlist_name

    music_library_path = '/Users/alvin/Library/RoonMounts/RoonStorage_0c6bb877af2e490f8941fe38db940a9ba30a2572/Music Section'
    sdcard_path = os.getcwd()
    
    playlist_folder = '/Users/alvin/Library/RoonMounts/RoonStorage_0c6bb877af2e490f8941fe38db940a9ba30a2572/Music Section/Playlists'

    confirmation_sdcard = input(f"Will transfer music into {sdcard_path}, are you sure? (y/n): ")
    if confirmation_sdcard.lower() in ["y", "yes"] :
        for playlist_name in playlist_names:
            playlist_path = os.path.join(playlist_folder, playlist_name+".m3u8")
            new_playlist_path = os.path.join(sdcard_path, 'Playlists', playlist_name+".m3u")

            file_paths = read_m3u_playlist(playlist_path)
            copy_music_files(file_paths, music_library_path, sdcard_path, sdcard_path)
            create_new_playlist(playlist_path, new_playlist_path, music_library_path, sdcard_path)
    else:
        print("Program execution cancelled.")

if __name__ == "__main__":
    main()