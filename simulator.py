# This program make sure that the request send by the user_id
# is converted into a payload (we are going with a json format here)
# later this payload will be send to two devices
# 1. Satellite
# 2. Datacenter (cloud)
import asyncio
import hashlib
import json
import os
import random
import sqlite3
import sys
from datetime import datetime
from typing import Any, Dict, Tuple


class StorageSimulator:
    def __init__(self, storage_type: str, base_path: str):
        self.storage_type = storage_type
        self.base_path = base_path
        # Use absolute path for the database
        self.db_path = os.path.join(
            os.path.expanduser("~"), "ef_hackathon", "satellite_data.db"
        )
        print(f"Using database at: {self.db_path}")  # Debug print
        self.locations = [
            "NYC",
            "LA",
            "Chicago",
            "Houston",
            "Miami",
            "Seattle",
            "Boston",
            "Denver",
        ]

    def initialize_db(self):
        """Initialize the database with required table"""
        print(f"Initializing database at {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS satellite_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE,
                timestamp TEXT NOT NULL,
                data_url TEXT NOT NULL,
                location TEXT
            )
        """
        )

        # Add some sample data if the table is empty
        cursor.execute("SELECT COUNT(*) FROM satellite_data")
        if cursor.fetchone()[0] == 0:
            print("Adding sample data...")
            sample_data = [
                ("file1", "2024-01-01T00:00:00Z", "https://example.com/data1", "NYC"),
                ("file2", "2024-01-02T00:00:00Z", "https://example.com/data2", "LA"),
                (
                    "file3",
                    "2024-01-03T00:00:00Z",
                    "https://example.com/data3",
                    "Chicago",
                ),
            ]
            cursor.executemany(
                """
                INSERT OR IGNORE INTO satellite_data (file_id, timestamp, data_url, location)
                VALUES (?, ?, ?, ?)
            """,
                sample_data,
            )

        conn.commit()
        conn.close()

    def add_random_locations(self):
        """Add random locations to records that don't have them"""
        if not os.path.exists(self.db_path):
            print(f"Database not found at {self.db_path}")
            self.initialize_db()

        print(f"Opening database at {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='satellite_data'
        """
        )
        if not cursor.fetchone():
            print("Table 'satellite_data' not found. Initializing database...")
            conn.close()
            self.initialize_db()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

        # Update locations
        cursor.execute("SELECT file_id FROM satellite_data WHERE location IS NULL")
        files = cursor.fetchall()

        for file_id in files:
            location = random.choice(self.locations)
            cursor.execute(
                """
                UPDATE satellite_data 
                SET location = ?
                WHERE file_id = ?
                """,
                (location, file_id[0]),
            )

        conn.commit()
        conn.close()

    async def send_to_satellite(self, file_path: str):
        """Mock satellite data request"""
        return {
            "status": "success",
            "source": "satellite",
            "request_timestamp": datetime.now().isoformat(),
            "results": [],
        }

    async def send_to_cloud(self, file_path: str) -> Dict[str, Any]:
        """Query the database for matching records"""
        try:
            with open(os.path.join(self.base_path, file_path), "r") as f:
                data = json.load(f)

            query_params = data.get("data", {}).get("query", {})
            location = query_params.get("location")
            start_time = query_params.get("start_time")
            end_time = query_params.get("end_time")

            print(f"\nQuerying with parameters:")
            print(f"Location: {location}")
            print(f"Start time: {start_time}")
            print(f"End time: {end_time}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Debug prints
            cursor.execute("SELECT * FROM satellite_data LIMIT 1")
            print(
                "Database schema:",
                [description[0] for description in cursor.description],
            )

            cursor.execute("SELECT COUNT(*) FROM satellite_data")
            count = cursor.fetchone()[0]
            print(f"Total records in database: {count}")

            cursor.execute("SELECT DISTINCT location FROM satellite_data")
            available_locations = cursor.fetchall()
            print(
                "\nAvailable locations in database:",
                [loc[0] for loc in available_locations],
            )

            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM satellite_data")
            time_range = cursor.fetchone()
            print(f"Database time range: {time_range[0]} to {time_range[1]}")

            query = """
                SELECT timestamp, data_url, location 
                FROM satellite_data 
                WHERE location = ?
                AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            """

            cursor.execute(query, (location, start_time, end_time))
            results = cursor.fetchall()

            print(f"\nFound {len(results)} matching records")

            if not results:
                raise Exception(
                    f"No data found for location {location} between {start_time} and {end_time}"
                )

            formatted_results = [
                {"capture_timestamp": timestamp, "data_url": url, "location": loc}
                for timestamp, url, loc in results
            ]

            conn.close()
            return {
                "status": "success",
                "source": "cloud",
                "request_timestamp": datetime.now().isoformat(),
                "results": formatted_results,
            }

        except Exception as e:
            print(f"Error in send_to_cloud: {str(e)}")
            raise

    async def process_payload(
        self, payload: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Process the incoming payload and return results"""
        try:
            file_path = self.generate_file_path(payload)
            self.write_to_file(payload, file_path)

            try:
                response = await self.send_to_cloud(file_path)
            except Exception as cloud_error:
                print(f"Cloud error: {cloud_error}")
                response = await self.send_to_satellite(file_path)

            return file_path, response
        except Exception as e:
            return "", {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error_message": str(e),
                "message": "Failed to store payload",
            }

    def generate_file_path(self, data: Dict[str, Any]) -> str:
        """Generate a unique file path for storing the request"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(json.dumps(data).encode()).hexdigest()[:8]
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{content_hash}_{unique_id}.json"

    def write_to_file(self, data: Dict[str, Any], file_path: str) -> None:
        """Write the payload to a file"""
        full_path = os.path.join(self.base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


async def main():
    """Main entry point for the script"""
    print("Starting simulator...")

    try:
        input_data = sys.stdin.read()
        print(f"Received input: {input_data}")

        payload = json.loads(input_data)
        print(f"Parsed payload: {json.dumps(payload, indent=2)}")

        storage_dir = os.path.join(
            os.path.expanduser("~"), "ef_hackathon", "data_storage"
        )
        os.makedirs(storage_dir, exist_ok=True)

        simulator = StorageSimulator("hybrid", storage_dir)
        simulator.add_random_locations()

        file_path, response = await simulator.process_payload(payload)
        print("Final response:", json.dumps(response, indent=2))
        print(json.dumps(response))  # This is what gets sent back to Node.js

    except Exception as e:
        error_response = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error_message": str(e),
            "message": "Failed to process request",
        }
        print(json.dumps(error_response))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
