import os
import shutil
import argparse
import unicodedata
from tqdm import tqdm
import ipaddress
from asyncio import run
import subprocess

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

async def copy_music_files(file_paths, src_base_path, dest_base_path, sdcard_path):
    for file_path in tqdm(file_paths, desc="Copying files"):
        if not file_path.startswith('#'):  # Only process non-comment lines
            file_path = file_path[3:] # TODO: Should change this into a more robust way using relpath
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

                folder_status = await check_file_exists_on_device(dest_folder)
                if not folder_status:
                    # await android_device.shell(f"mkdir -p \"{dest_folder}\"",transport_timeout_s=300, read_timeout_s=300, timeout_s=300)
                    subprocess.run(['adb', 'shell', f'mkdir -p "{dest_folder}"'], capture_output=True, text=True, check=True)
                    # os.makedirs(dest_folder)

                # if not os.path.exists(dest_sanitized):
                file_status = await check_file_exists_on_device(dest_sanitized)
                # tqdm.write(f"file_status is {file_status}, Now checking: {dest_sanitized}")
                if not file_status:
                    # shutil.copy2(src, dest_sanitized)
                    # await android_device.push(src, dest_sanitized, read_timeout_s=300)
                    subprocess.run(['adb', 'push', src, dest_sanitized], capture_output=True, text=True, check=True)
                    tqdm.write(f"Copied: {src} to {dest_sanitized}")
                # else:
                #     tqdm.write(f"Skipped: (already exists): {dest}")

                # # Handle duplicate names after sanitization
                # if dest != dest_sanitized:
                #     dest_sanitized_folder = os.path.dirname(dest_sanitized)
                #     # dest_sanitized = os.path.join(dest_sanitized_folder, unique_name(dest_folder, os.path.basename(dest_sanitized)))
                #     if not os.path.exists(dest_sanitized_folder):
                #         os.makedirs(dest_sanitized_folder)

                #     shutil.move(dest, dest_sanitized)
                #     print(f"Renamed: {dest} to {dest_sanitized}")