import os
import shutil
import argparse
import unicodedata
from tqdm import tqdm
import ipaddress
from asyncio import run
import subprocess
import json

from walkman import check_file_exists_on_device, copy_music_files_adb, create_new_playlist_adb
from playlist import copy_music_files, create_new_playlist

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def read_m3u_playlist(file_path, ignore_tags=True):
    with open(file_path, 'r') as file:
        if not ignore_tags:
            return [line.strip() for line in file if not line.startswith('#')]
        return [line.strip() for line in file]
    
def sanitize_name(name):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '：', '・','　'] # Actually last 3 are valid but i don't like it
    new_name = name.rstrip('.').replace('...', '..')

    for char in invalid_chars:
        new_name = new_name.replace(char, '_')
    new_name = unicodedata.normalize('NFC', new_name) # Needed if using macOS or it won't work on Android

    return new_name

def unique_name(destination, original_name):
    base, ext = os.path.splitext(original_name)
    counter = 1
    new_name = original_name
    while os.path.exists(os.path.join(destination, new_name)):
        new_name = f"{base}_{counter}{ext}"
        counter += 1
    return new_name

async def main():
    parser = argparse.ArgumentParser(description='Copy music files and create playlists.')
    parser.add_argument('playlist_name', nargs='+', help='Name of the playlist file(s) (with or without .m3u extension)')
    parser.add_argument('--mode','-m', required=True, help='Mode to use (adb or local)')

    args = parser.parse_args()
    playlist_names = args.playlist_name
    mode = args.mode
    if mode not in ['adb', 'local']:
        raise ValueError("Mode must be either adb or local")
    
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        music_library_path = config['music_library']

    playlist_folder = os.path.join(music_library_path, 'Playlists')

    if mode == 'adb':
        storage_list = subprocess.run(['adb', 'shell', 'ls', '/storage'], capture_output=True, text=True, check=True).stdout
        confirmation_sdcard_mount = input(f"Found SD Card /storage/{storage_list.split()[0].strip()}, are you sure? (y/n): ")
        if confirmation_sdcard_mount.lower() in ["y", "yes"] :
            sdcard_path = f"/storage/{storage_list.split()[0].strip()}/Music"
        else:
            print("Program execution cancelled.")
            return

        confirmation_sdcard = input(f"Will transfer music into {sdcard_path}, are you sure? (y/n): ")
        if confirmation_sdcard.lower() in ["y", "yes"] :
            for playlist_name in playlist_names:
                playlist_path = os.path.join(playlist_folder, playlist_name+".m3u8")
                new_playlist_path = os.path.join(sdcard_path, 'Playlists', playlist_name+".m3u")

                file_paths = read_m3u_playlist(playlist_path)
                await copy_music_files_adb(file_paths, music_library_path, sdcard_path, sdcard_path)
                await create_new_playlist_adb(playlist_path, new_playlist_path, music_library_path, sdcard_path)
        else:
            print("Program execution cancelled.")
    else:
        sdcard_path = os.getcwd()
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
    run(main())
