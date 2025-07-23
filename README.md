
# Spedion API File Sender

![Spedion API Automation](docs/Automatisierter_Dateiversand_mit_Spedion_API.png)

This Python script automates sending files to the Spedion InformationExchange API.  
It scans a source folder, sends each file as a message with attachment to a specific driver (parsed from the file name), and saves logs and request JSONs.  
All configuration and credentials are stored in a separate `config.json` file.

## Features

- **Automatic file scanning and sending:**  
  Scans a given folder for files and sends each file as a message to the Spedion API, using file name to determine driver data.

- **Presigned upload:**  
  Uploads each file to the server using presigned URLs provided by the API.

- **Personalized messaging:**  
  The script generates a personalized message for each driver based on file name.

- **Logging:**  
  Detailed logs are written for all actions (processing, upload, sending, errors) into a daily rotating log file.

- **Result archiving:**  
  Sent files are moved to a backup folder, and request JSONs are saved to a separate folder, all with timestamps for traceability.

- **Configuration separation:**  
  All credentials and paths are taken from `config.json` (not included in repo for security).

---

## File name format

The file name must follow the format:

```
<driverPin>_<FirstName>_<LastName>.<ext>
```
**Example:**  
`12345_Max_Mustermann.pdf`

---

## Configuration (`config.json`)

Create a `config.json` file in the project directory, for example:

```json
{
    "API_URL": "https://services.spedion.de/InformationExchangeWS/1.0",
    "USERNAME": "YOUR_USERNAME",
    "PASSWORD": "YOUR_PASSWORD",
    "FOLDER": "/path/to/input",
    "SENT_FOLDER": "/path/to/sent",
    "JSON_FOLDER": "/path/to/json",
    "LOG_PATH": "/path/to/log"
}
```

**Do NOT commit `config.json` to the repository!**  
Add it to your `.gitignore`:

```
config.json
```

---

## Usage

1. Install requirements (if needed):

   ```
   pip install requests
   ```

2. Copy and edit `config.json` as shown above.

3. Run the script:

   ```
   python main.py
   ```

---

## How it works

- For each file in the input folder:
  - Parses driver pin, first and last name from the file name.
  - Gets presigned URLs from Spedion API.
  - Uploads the file.
  - Sends the message with attachment (including personalized text).
  - On successful send:
    - Moves the file to the archive folder (with timestamp in name).
    - Saves the request JSON to the JSON folder (also with timestamp).
  - All steps and errors are logged to a daily log file.

---

## License

MIT License

---

If you need help or want to suggest improvements, open an issue or pull request!
