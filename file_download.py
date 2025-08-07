"""
import os
import requests


def main():
    fileURL = (
        "https://baseten-public.s3.us-west-2.amazonaws.com/sample-app-building.mp4"
    )
    numBatches = 4

    fileSize = get_file_size(fileURL)
    if fileSize is None:
        print("Failed to retrieve file size")
        return
    print("File size:", fileSize)

    if not download_file_in_batches(fileURL, numBatches):
        print("Failed to download file")
        return
    print("File downloaded successfully")


def get_file_size(fileURL):
    resp = requests.head(fileURL)
    if resp.status_code != 200:
        return None

    fileSize = int(resp.headers.get("Content-Length", 0))
    return fileSize


def download_byte_range(index, fileURL, startByte, endByte):
    headers = {}
    if endByte != -1:
        headers["Range"] = f"bytes={startByte}-{endByte}"

    resp = requests.get(fileURL, headers=headers)
    if resp.status_code != 206:
        return False

    with open(f"part{index}.bin", "wb") as file:
        file.write(resp.content)

    return True


def download_file_in_batches(fileURL, numBatches):
    fileSize = get_file_size(fileURL)
    if fileSize is None:
        return False

    chunkSize = fileSize // numBatches

    with open("downloaded_file.bin", "wb") as file:
        for i in range(numBatches):
            startByte = i * chunkSize
            endByte = startByte + chunkSize - 1 if i < numBatches - 1 else fileSize - 1

            if not download_byte_range(i, fileURL, startByte, endByte):
                return False

            with open(f"part{i}.bin", "rb") as partFile:
                file.write(partFile.read())

            os.remove(f"part{i}.bin")

    return True


if __name__ == "__main__":
    main()
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

def main():
    fileURL = "https://baseten-public.s3.us-west-2.amazonaws.com/sample-app-building.mp4"
    numBatches = 4

    fileSize = get_file_size(fileURL)
    if fileSize is None:
        print("Failed to retrieve file size")
        return

    print("File size:", fileSize)

    if not download_file_in_batches(fileURL, fileSize, numBatches):
        print("Failed to download file")
        return

    print("File downloaded successfully")


def get_file_size(fileURL):
    resp = requests.head(fileURL)
    if resp.status_code != 200:
        return None

    fileSize = int(resp.headers.get("Content-Length", 0))
    return fileSize


def download_byte_range(index, fileURL, startByte, endByte):
    headers = {}
    if endByte != -1:
        headers["Range"] = f"bytes={startByte}-{endByte}"

    resp = requests.get(fileURL, headers=headers)
    if resp.status_code != 206:
        return False

    with open(f"part{index}.bin", "wb") as file:
        file.write(resp.content)

    return True


def download_file_in_batches(fileURL, fileSize, numBatches):
    chunkSize = fileSize // numBatches
    with ThreadPoolExecutor(max_workers=numBatches) as executor:
        futures = []

        for i in range(numBatches):
            startByte = i * chunkSize
            endByte = (startByte + chunkSize - 1) if i < numBatches - 1 else fileSize - 1
            futures.append(executor.submit(download_byte_range, i, fileURL, startByte, endByte))

        for future in as_completed(futures):
            result = future.result()
            if result is None:
                return False

    with open("downloaded_file.bin", "wb") as file:
        for i in range(numBatches):
            with open(f"part{i}.bin", "rb") as partFile:
                file.write(partFile.read())
            os.remove(f"part{i}.bin")
    
    return True


if __name__ == "__main__":
    main()


"""
(base) hockshanwong@Mac code % shasum -a 256 downloaded_file.bin
00868ce860cefa84564869b9b79b10022b1059bba89853e6045cdaa6ee1eefd4  downloaded_file.bin


(base) hockshanwong@Mac code % curl -O "https://baseten-public.s3.us-west-2.amazonaws.com/sample-app-building.mp4"

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 9905k  100 9905k    0     0  6034k      0  0:00:01  0:00:01 --:--:-- 6032k
(base) hockshanwong@Mac code % ls -lrt


(base) hockshanwong@Mac code % shasum -a 256 sample-app-building.mp4
00868ce860cefa84564869b9b79b10022b1059bba89853e6045cdaa6ee1eefd4  sample-app-building.mp4


"""



