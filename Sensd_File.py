import os
import shutil
import json
import requests
from datetime import datetime

# --- Load configuration ---
with open("config.json", "r", encoding="utf-8") as conf:
    CONFIG = json.load(conf)

API_URL = CONFIG["API_URL"]
USERNAME = CONFIG["USERNAME"]
PASSWORD = CONFIG["PASSWORD"]
FOLDER = CONFIG["FOLDER"]
SENT_FOLDER = CONFIG["SENT_FOLDER"]
JSON_FOLDER = CONFIG["JSON_FOLDER"]
LOG_PATH = CONFIG["LOG_PATH"]

os.makedirs(SENT_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)

def WRITELOG(log_txt):
    noww = datetime.now()
    DDtSt = str(noww.strftime("%Y%m%d")).replace(' ','')
    DDMiSt = str(noww.strftime("%d-%m-%Y %H:%M"))
    with open(f'{LOG_PATH}/{DDtSt}Spedion_send_files.log', 'a', encoding="utf-8") as log:
        log.write(f'[{DDMiSt} Spedion.log] ' + log_txt +'\n')
    print(log_txt)

# ... other functions remain unchanged ...

def get_presigned_url(api_url, filename, filesize):
    data = {
        "filename": filename,
        "filesize": int(filesize),
        "indicator": 0
    }
    WRITELOG(f"PresignedUploadUrl-Request: {json.dumps(data)}")
    response = requests.post(
        f"{api_url}/api/PresignedAttachmentUploadUrl",
        json=data,
        auth=(USERNAME, PASSWORD)
    )
    WRITELOG(f"PresignedUploadUrl-Response: {response.text}")
    response.raise_for_status()
    return response.json()['uploadUrl'], response.json()['downloadUrl']

def upload_file(upload_url, filepath):
    with open(filepath, 'rb') as f:
        file_data = f.read()
    response = requests.put(upload_url, data=file_data)
    response.raise_for_status()

def send_information(api_url, sender, driver_pin, message, attachment_name, attachment_type, attachment_url):
    data = {
        "sender": sender,
        "receiver": {
            "driverPin": driver_pin
        },
        "message": message,
        "attachments": [
            {
                "name": attachment_name,
                "type": attachment_type,
                "url": attachment_url
            }
        ],
        "tag": "SendTextMessage"
    }
    response = requests.put(
        f"{api_url}/api/SendInformation",
        json=data,
        auth=(USERNAME, PASSWORD)
    )
    # If status code is 200 - OK, otherwise raise exception
    return response, data

def parse_filename(filename):
    base = os.path.splitext(filename)[0]
    parts = base.split('_')
    if len(parts) < 3:
        raise ValueError(f"Filename '{filename}' must follow the format DriverPin_FirstName_LastName.ext")
    driver_pin = parts[0]
    first_name = parts[1]
    last_name = "_".join(parts[2:])
    return driver_pin, first_name, last_name

def move_file(src, dst_folder):
    # Add timestamp in format YYYYMMDDSSmm before the filename
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%S%M")
    filename = os.path.basename(src)
    new_filename = f"{timestamp}_{filename}"
    dst = os.path.join(dst_folder, new_filename)
    shutil.move(src, dst)
    return dst

def save_json(data, filename, folder):
    # Add timestamp in format YYYYMMDDSSmm before the filename
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%S%M")
    base_name = os.path.splitext(filename)[0]
    name = f"{timestamp}_{base_name}.json"
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def main():
    for filename in os.listdir(FOLDER):
        filepath = os.path.join(FOLDER, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            driver_pin, first_name, last_name = parse_filename(filename)
            filesize = os.path.getsize(filepath)
            WRITELOG(f"Processing file: {filename} for driver {driver_pin} ({first_name} {last_name})")

            # 1. Request presigned upload/download URLs
            upload_url, download_url = get_presigned_url(API_URL, filename, filesize)
            WRITELOG("Presigned URLs received.")

            # 2. Upload the file
            upload_file(upload_url, filepath)
            WRITELOG(f"File {filename} uploaded.")

            # 3. Send information
            sender = {"firstName": first_name, "lastName": last_name}
            message = f"Hello {first_name} {last_name},\nplease find the attached document."
            attachment_name = os.path.splitext(filename)[0]
            attachment_type = os.path.splitext(filename)[1][1:]  # without dot
            attachment_url = download_url

            response, json_data = send_information(
                API_URL, sender, driver_pin, message, attachment_name, attachment_type, attachment_url
            )
            if response.status_code == 200:
                WRITELOG(f"File {filename} successfully sent! Response: {response.text}")
                # Save JSON
                json_path = save_json(json_data, filename, JSON_FOLDER)
                WRITELOG(f"JSON saved: {json_path}")
                # Move file only if successful!
                try:
                    sent_path = move_file(filepath, SENT_FOLDER)
                    WRITELOG(f"File moved to: {sent_path}")
                except Exception as e:
                    WRITELOG(f"Error moving file {filename}: {e}")
            else:
                WRITELOG(f"Error sending file {filename}: SendInformation status_code={response.status_code}, Response: {response.text}")

        except Exception as e:
            WRITELOG(f"Error processing file {filename}: {e}")

if __name__ == "__main__":
    main()
