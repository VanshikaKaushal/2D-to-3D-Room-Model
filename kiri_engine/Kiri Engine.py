import os
import time
import zipfile
import requests
from pathlib import Path
from contextlib import ExitStack
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.kiriengine.app/api"
API_KEY = os.environ.get("KIRI_API_KEY")

if not API_KEY:
    raise RuntimeError("KIRI_API_KEY not found. Check your .env file.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

VALID_EXTS = {".jpg", ".jpeg", ".png"}


# This means the Test folder should be in the same folder as this Python file
BASE_DIR = Path(__file__).resolve().parent
TEST_DIR = BASE_DIR / "Test"
OUTPUT_ROOT = TEST_DIR / "Output"


def get_images(folder_path):
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Folder does not exist: {folder}")

    images = sorted([
        p for p in folder.iterdir()
        if p.suffix.lower() in VALID_EXTS
    ])

    if not (20 <= len(images) <= 300):
        raise ValueError(
            f"KIRI Photo Scan expects 20 to 300 images. Found: {len(images)}"
        )

    return images


def upload_images(folder_path, model_quality=1, texture_quality=1, file_format="GLB",
                  is_mask=1, texture_smoothing=1):
    images = get_images(folder_path)

    total_size_mb = sum(img.stat().st_size for img in images) / (1024 * 1024)

    print(f"Found {len(images)} images.")
    print(f"Total upload size: {total_size_mb:.2f} MB")
    print("Sending images to KIRI. This may take a few minutes...")

    url = f"{BASE_URL}/v1/open/photo/image"

    data = {
        "modelQuality": str(model_quality),        # 0 High, 1 Medium, 2 Low, 3 Ultra
        "textureQuality": str(texture_quality),    # 0 4K, 1 2K, 2 1K, 3 8K
        "fileFormat": file_format,                 # OBJ, FBX, STL, PLY, GLB, GLTF, USDZ, XYZ
        "isMask": str(is_mask),                    # 0 off, 1 on
        "textureSmoothing": str(texture_smoothing)
    }

    with ExitStack() as stack:
        files = []

        for img in images:
            f = stack.enter_context(open(img, "rb"))
            files.append(("imagesFiles", (img.name, f, "application/octet-stream")))

        response = requests.post(
            url,
            headers=HEADERS,
            data=data,
            files=files,
            timeout=600
        )

        response.raise_for_status()
        result = response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Upload failed: {result}")

    serialize = result["data"]["serialize"]
    return serialize


def get_status(serialize):
    url = f"{BASE_URL}/v1/open/model/getStatus"

    response = requests.get(
        url,
        headers=HEADERS,
        params={"serialize": serialize},
        timeout=60
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Status check failed: {result}")

    return result["data"]["status"]


def wait_until_done(serialize, poll_seconds=30):
    status_map = {
        -1: "Uploading",
         0: "Processing",
         1: "Failed",
         2: "Successful",
         3: "Queuing",
         4: "Expired"
    }

    while True:
        status = get_status(serialize)

        print(f"Current status: {status} ({status_map.get(status, 'Unknown')})")

        if status == 2:
            return

        elif status in (1, 4):
            raise RuntimeError(
                f"Task ended with status {status}: {status_map.get(status)}"
            )

        time.sleep(poll_seconds)


def get_download_url(serialize):
    url = f"{BASE_URL}/v1/open/model/getModelZip"

    response = requests.get(
        url,
        headers=HEADERS,
        params={"serialize": serialize},
        timeout=60
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Download URL fetch failed: {result}")

    return result["data"]["modelUrl"]


def download_and_extract_model(download_url, output_dir, zip_name="kiri_model.zip"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = output_dir / zip_name

    print(f"Downloading zip to: {zip_path}")

    with requests.get(download_url, stream=True, timeout=600) as r:
        r.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print("Extracting zip...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    print(f"Model saved and extracted to: {output_dir}")

    return output_dir


def run_pipeline(images_folder, output_dir):
    print("\nUploading images...")
    serialize = upload_images(images_folder)

    print(f"\nTask created.")
    print(f"Serialize ID: {serialize}")

    print("\nWaiting for model generation...")
    wait_until_done(serialize)

    print("\nFetching download URL...")
    download_url = get_download_url(serialize)

    print("\nDownloading and extracting model...")
    download_and_extract_model(download_url, output_dir)

    print("\nDone!")
    print(f"Check your files here: {output_dir}")


def choose_room_folder():
    if not TEST_DIR.exists() or not TEST_DIR.is_dir():
        raise ValueError(
            f"Test folder does not exist.\n"
            f"Create a folder named 'Test' here:\n{BASE_DIR}"
        )

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    available_folders = [
        p.name for p in TEST_DIR.iterdir()
        if p.is_dir() and p.name.lower() != "output"
    ]

    if not available_folders:
        raise ValueError(
            f"No room folders found inside:\n{TEST_DIR}\n"
            f"Create folders like Room1, Room2, Room3 inside Test."
        )

    print("\nAvailable folders inside Test:")
    for folder in available_folders:
        print(f"- {folder}")

    folder_name = input("\nEnter the room folder name exactly as shown above: ").strip()

    images_folder = TEST_DIR / folder_name

    if not images_folder.exists() or not images_folder.is_dir():
        raise ValueError(f"Folder not found: {images_folder}")

    output_dir = OUTPUT_ROOT / f"{folder_name}_output"

    return images_folder, output_dir


if __name__ == "__main__":
    images_folder, output_dir = choose_room_folder()

    print("\nSelected folder:")
    print(images_folder)

    print("\nOutput will be saved to:")
    print(output_dir)

    run_pipeline(images_folder, output_dir)