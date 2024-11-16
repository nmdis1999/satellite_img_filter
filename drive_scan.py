import os
import pickle
import random
import sqlite3
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER_ID = "1Hw2x_vg5r567TFiGy4fLhwxxZCuyHPU7"


class DriveScanner:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.creds = self.get_credentials()
        self.service = build("drive", "v3", credentials=self.creds)
        self.cities = [
            "NYC",
            "LA",
            "Chicago",
            "Houston",
            "Miami",
            "Seattle",
            "Boston",
            "Denver",
            "Austin",
            "Portland",
            "Dallas",
            "Atlanta",
            "Phoenix",
            "Detroit",
        ]
        self.initialize_db()

    def get_credentials(self):
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return creds

    def initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS satellite_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE,
                timestamp TEXT NOT NULL,
                data_url TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """
        )
        conn.commit()
        conn.close()

    def scan_folder(self):
        query = f"'{FOLDER_ID}' in parents"
        new_entries = 0
        updated_entries = 0
        page_token = None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        while True:
            response = (
                self.service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, createdTime, webViewLink)",
                    pageToken=page_token,
                )
                .execute()
            )

            for file in response.get("files", []):
                file_id = file["id"]
                file_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
                location = random.choice(self.cities)

                cursor.execute(
                    "SELECT id FROM satellite_data WHERE file_id = ?", (file_id,)
                )
                exists = cursor.fetchone()

                if exists:
                    cursor.execute(
                        """
                        UPDATE satellite_data 
                        SET timestamp = ?, data_url = ?, location = ?
                        WHERE file_id = ?
                    """,
                        (file["createdTime"], file_url, location, file_id),
                    )
                    updated_entries += 1
                else:
                    cursor.execute(
                        """
                        INSERT INTO satellite_data (file_id, timestamp, data_url, location)
                        VALUES (?, ?, ?, ?)
                    """,
                        (file_id, file["createdTime"], file_url, location),
                    )
                    new_entries += 1

            conn.commit()
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        conn.close()
        return new_entries, updated_entries

    def get_all_entries(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, data_url, location 
            FROM satellite_data 
            ORDER BY timestamp DESC
        """
        )
        results = cursor.fetchall()
        conn.close()
        return [
            {"timestamp": row[0], "url": row[1], "location": row[2]} for row in results
        ]


def main():
    db_path = "satellite_data.db"
    scanner = DriveScanner(db_path)

    print("Scanning folder and updating database...")
    new, updated = scanner.scan_folder()
    print(f"New entries added: {new}")
    print(f"Entries updated: {updated}")

    print("\nAll entries in database:")
    entries = scanner.get_all_entries()
    for entry in entries:
        print(f"Timestamp: {entry['timestamp']}")
        print(f"URL: {entry['url']}")
        print(f"Location: {entry['location']}\n")


if __name__ == "__main__":
    main()
