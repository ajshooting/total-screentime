import sqlite3
import glob
import os
import datetime

# ! デバッグ用
import pprint


def find_latest_db_file():
    db_files = glob.glob(
        "/private/var/folders/*/*/0/com.apple.ScreenTimeAgent/Store/RMAdminStore-Local.sqlite",
        recursive=True,
    )
    if not db_files:
        return None

    # 複数あったら最新のやつ
    latest_db_file = max(db_files, key=os.path.getmtime)
    return latest_db_file


def extract_data(db_file):
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
        SELECT
            IFNULL(utimed.ZBUNDLEIDENTIFIER, utimed.ZDOMAIN) as app,
            utimed.ZTOTALTIMEINSECONDS as total_time,
            datetime(ublock.ZFIRSTPICKUPDATE + 978307200, 'unixepoch') as first_pickup_date,
            datetime(ublock.ZSTARTDATE + 978307200, 'unixepoch') as start_date,
            datetime(ublock.ZLASTEVENTDATE + 978307200, 'unixepoch') as last_event_date,
            ucounted.ZNUMBEROFNOTIFICATIONS as notifications,
            ucounted.ZNUMBEROFPICKUPS as pickups,
            ublock.ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE as pickups_no_use,
            ublock.ZSCREENTIMEINSECONDS as screentime_seconds,
            cdevice.ZNAME as device_name,
            cuser.ZAPPLEID as apple_id,
            cuser.ZGIVENNAME as given_name,
            cuser.ZFAMILYNAME as family_name,
            cuser.ZFAMILYMEMBERTYPE as family_type
        FROM ZUSAGETIMEDITEM as utimed
            LEFT JOIN ZUSAGECATEGORY as ucategory on ucategory.Z_PK = utimed.ZCATEGORY
            LEFT JOIN ZUSAGEBLOCK as ublock on ublock.Z_PK = ucategory.ZBLOCK
            LEFT JOIN ZUSAGE as usage on usage.Z_PK = ublock.ZUSAGE
            LEFT JOIN ZCOREDEVICE as cdevice on cdevice.Z_PK = usage.ZDEVICE
            LEFT JOIN ZCOREUSER as cuser on cuser.Z_PK = usage.ZUSER
            LEFT JOIN ZUSAGECOUNTEDITEM as ucounted on ucounted.ZBLOCK = ucategory.ZBLOCK AND ucounted.ZBUNDLEIDENTIFIER = utimed.ZBUNDLEIDENTIFIER
        ORDER BY ublock.ZSTARTDATE
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("No data found in the database.")
            conn.close()
            return

        data = []

        data.append(rows[0].keys())

        for row in rows:
            data.append([row[key] for key in row.keys()])

        # ! デバッグ用
        pprint.pp(data)

        return data

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def main():
    db_file = find_latest_db_file()

    if db_file:
        print(f"Database file found: {db_file}")
        data = extract_data(db_file)
    else:
        print("No matching database file found.")
    
    


if __name__ == "__main__":
    main()
