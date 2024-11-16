import json
import sqlite3
from datetime import datetime


class DatabaseViewer:
    def __init__(self, db_path: str = "satellite_data.db"):
        self.db_path = db_path

    def view_all_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA table_info(satellite_data)")
            columns = [column[1] for column in cursor.fetchall()]
            print("\nTable Columns:", columns)

            cursor.execute("SELECT * FROM satellite_data ORDER BY timestamp DESC")
            rows = cursor.fetchall()

            print(f"\nTotal Entries: {len(rows)}")
            print("\nDatabase Contents:")
            print("-" * 100)

            for row in rows:
                data = dict(zip(columns, row))
                print(
                    f"""
ID: {data['id']}
File ID: {data['file_id']}
Timestamp: {data['timestamp']}
Location: {data['location']}
URL: {data['data_url']}
{'-' * 100}"""
                )

            # Print statistics
            print("\nStatistics:")
            cursor.execute(
                "SELECT location, COUNT(*) as count FROM satellite_data GROUP BY location"
            )
            location_stats = cursor.fetchall()
            print("\nImages per location:")
            for location, count in location_stats:
                print(f"{location}: {count}")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def view_by_location(self, location: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM satellite_data 
                WHERE location = ? 
                ORDER BY timestamp DESC
            """,
                (location,),
            )

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            print(f"\nEntries for location {location}: {len(rows)}")

            for row in rows:
                data = dict(zip(columns, row))
                print(
                    f"""
ID: {data['id']}
Timestamp: {data['timestamp']}
URL: {data['data_url']}
{'-' * 50}"""
                )

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()


def main():
    viewer = DatabaseViewer()

    while True:
        print("\nDatabase Viewer Options:")
        print("1. View all data")
        print("2. View data by location")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ")

        if choice == "1":
            viewer.view_all_data()
        elif choice == "2":
            location = input("Enter location (e.g., NYC, LA, Chicago): ")
            viewer.view_by_location(location)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
