# WMSync

WMSync is a tool for syncing music files and m3u/m3u8 playlists to Walkman devices or other music players.

## Features

- Two modes: Local mode and ADB mode
- Local mode: Copies files from a local path on the computer to another local path (mounted network places allowed)
- ADB mode: Copies files from a local path to an Android device using ADB

## Getting Started

### Prerequisites

- ADB should be installed from Android SDK
- [ADB (Android Debug Bridge)](https://developer.android.com/studio/command-line/adb)

### Usage

### Setup

1. `pip install tqdm`

2. Create a json file under current directory named `config.json` with the following content:

```json
{
    "music_library": "<path-to-your-music-library>"
}
```

3. make sure your m3u/m3u8 playlists are stored at `<path-to-your-music-library>/Playlists`

4. make sure your destination folder has a folder named `Playlists` as well.

#### Local Mode

```python playlist.py [-h] playlist_name [playlist_name ...]```

#### ADB Mode

ADB Mode basically works the same as local mode but you have to make sure your android device is connected to your computer and ADB is enabled. You can check it by typing `adb devices`.

```python walkman.py [-h] playlist_name [playlist_name ...]```

or

you can run either these 2 modes from `wmsync.py` by providing the mode with `--mode` or `-m` argument.

## License

This project is licensed under the [MIT License](LICENSE).

