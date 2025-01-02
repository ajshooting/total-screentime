import sqlite3
import glob
import os
import shutil
import datetime


def find_latest_db_file():
    db_files = glob.glob(
        "/private/var/folders/*/*/0/com.apple.ScreenTimeAgent/Store/RMAdminStore-Local.sqlite",
        recursive=True,
    )
    if not db_files:
        return None

    # 複数当たったら最新のやつ
    latest_db_file = max(db_files, key=os.path.getmtime)
    return latest_db_file


def backup_db_file(db_file, backup_dir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"RMAdminStore-Local_{timestamp}.sqlite"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        shutil.copy2(db_file, backup_path) 
        print(f"Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Error during backup: {e}")
        return None


def extract_data(db_file, output_dir):
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row  # カラム名でアクセスできるようにする
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

        # CSVファイルに書き込む
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"extracted_data_{timestamp}.csv"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            # ヘッダー行
            header = rows[0].keys()
            f.write(",".join(header) + "\n")

            # データ行
            for row in rows:
                f.write(",".join(str(row[col]) for col in header) + "\n")

        print(f"Data extracted to: {output_path}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def main():
    backup_dir = "./backup"
    output_dir = "./data"

    # ディレクトリが存在しない場合は作成する
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    db_file = find_latest_db_file()

    if db_file:
        print(f"Latest database file found: {db_file}")
        backup_db_file(db_file, backup_dir)
        extract_data(db_file, output_dir)
    else:
        print("No matching database file found.")


if __name__ == "__main__":
    main()
