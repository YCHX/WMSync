from adb_shell.adb_device import AdbDeviceUsb, AdbDeviceTcp
from adb_shell.adb_device_async import AdbDeviceTcpAsync
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import subprocess

from asyncio import run

async def main():

    storage_list = subprocess.run(['adb', 'shell', 'ls', '/storage'], capture_output=True, text=True, check=True).stdout
    print(storage_list.split()[0].strip())

run(main())