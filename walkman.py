import os
import shutil
import argparse
import unicodedata
from tqdm import tqdm
import ipaddress
from asyncio import run
import subprocess

# from adb_shell.adb_device_async import AdbDeviceTcpAsync
# from adb_shell.auth.sign_pythonrsa import PythonRSASigner

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
    
async def check_file_exists_on_device(file_path):
    command = f'test -e "{file_path}" && echo yes || echo no'
    # result = await device.shell(command, transport_timeout_s=300, read_timeout_s=300, timeout_s=300)
    result = subprocess.run(['adb', 'shell', command], capture_output=True, text=True, check=True).stdout
    return 'yes' in result

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

async def copy_music_files_adb(file_paths, src_base_path, dest_base_path, sdcard_path):
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


async def create_new_playlist_adb(original_playlist_path, new_playlist_path, src_base_path, dest_base_path):
    file_paths = read_m3u_playlist(original_playlist_path)
    with open(f"./{os.path.basename(new_playlist_path)}", 'w') as new_playlist:
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
    # await android_device.push(f"./{os.path.basename(new_playlist_path)}", new_playlist_path)
    subprocess.run(['adb', 'push', f"./{os.path.basename(new_playlist_path)}", new_playlist_path], capture_output=True, text=True, check=True)
    # Remove temporary file
    os.remove(f"./{os.path.basename(new_playlist_path)}")

async def main():
    parser = argparse.ArgumentParser(description='Copy music files and create playlists.')
    parser.add_argument('playlist_name', nargs='+', help='Name of the playlist file(s) (with or without .m3u extension)')
    # parser.add_argument('--android-ip', '-I', help='Android device IP address', required=True)
    # parser.add_argument('--port', '-p', help='Android device port', default=5555, required=True)


    args = parser.parse_args()
    playlist_names = args.playlist_name
    # android_ip = args.android_ip
    # port = args.port
    # if not is_valid_ip(android_ip):
    #     raise ValueError("Invalid IP address")

    music_library_path = '/Users/alvin/Library/RoonMounts/RoonStorage_0c6bb877af2e490f8941fe38db940a9ba30a2572/Music Section'
    # sdcard_path = os.getcwd()
    
    playlist_folder = '/Users/alvin/Library/RoonMounts/RoonStorage_0c6bb877af2e490f8941fe38db940a9ba30a2572/Music Section/Playlists'

    # adbkey = '/Users/alvin/.android/adbkey'
    # with open(adbkey) as f:
    #     priv = f.read()
    # with open(adbkey + '.pub') as f:
    #     pub = f.read()
    # signer = PythonRSASigner(pub, priv)

    # device2 = AdbDeviceTcpAsync(str(android_ip), port=int(port), default_transport_timeout_s=300)
    # await device2.connect(rsa_keys=[signer], auth_timeout_s=0.1)
    
    # if device2.available == False:
    #     raise RuntimeError('Device not available')

    # storage_list = await device2.shell("ls /storage", transport_timeout_s=300, read_timeout_s=300, timeout_s=300)
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
        # device2.close()

if __name__ == "__main__":
    run(main())