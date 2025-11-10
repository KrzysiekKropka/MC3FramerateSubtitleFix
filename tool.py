import os
import csv
import subprocess

BASE_FOLDER = os.getcwd()
SUBTITLE_FOLDER = os.path.join(BASE_FOLDER, "ASSETS", "tune", "subtitle")

def decompile_assets():
    print(f"Decompiling ASSETS.DAT...")
    subprocess.run(["python", "dave.py", "X", "ASSETS.DAT"], check=True)

def compile_assets():
    print(f"Compiling ASSETS.DAT...")
    try:
        subprocess.run(
            ["python", "dave.py", "B", "-ca", "-cn", "-cf", "-fc", "1", "ASSETS", "ASSETS.DAT"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("There was an error with dave.py compiling ASSETS.DAT. Check error above. Might need to run this script as an administrator.")

def process_csv(file_path, restore = False):
    rows = []

    # Try reading with multiple encodings
    for enc in ["utf-8-sig", "cp1252"]:
        try:
            with open(file_path, "r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    eng = row["English"].strip().lower()
                    if eng in ["time correction", "position", "size"]:
                        rows.append(row)
                        continue

                    # Double time code and end time if numeric
                    for col in ["Time Code", "end time"]:
                        try:
                            if row[col]:
                                if restore == True: row[col] = str(float(row[col]) * 0.5)
                                else: row[col] = str(float(row[col]) * 2)
                        except ValueError:
                            pass

                    rows.append(row)
            break  # if successful, stop trying encodings
        except UnicodeDecodeError:
            continue
    else:
        print(f"Could not do shit with {file_path}. Report back to TDFPL, he fucked up smth")
        return

    # Write back in UTF-8 to unify
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    if os.path.exists(os.path.join(BASE_FOLDER, "ASSETS.DAT")):
        answer = input("Do you want to decompile ASSETS.DAT? (Y/N) ").strip().lower()
        if answer == "y":
            decompile_assets()

    if not os.path.exists(SUBTITLE_FOLDER): 
        print(f"There is no {SUBTITLE_FOLDER}!")
        return

    if not os.path.exists(os.path.join(SUBTITLE_FOLDER, "subtitle.fix")):
        for root, _, files in os.walk(SUBTITLE_FOLDER):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    print(f"Doubling timecode values at {file_path}")
                    process_csv(file_path)
        open(os.path.join(SUBTITLE_FOLDER, "subtitle.fix"), "w").close()
    else:
        print("The timecodes are already fixed.")
        answer = input("Do you want to restore timecodes to original values for 30 FPS gameplay? (Y/N) ").strip().lower()
        if answer == "y":
            for root, _, files in os.walk(SUBTITLE_FOLDER):
                for file in files:
                    if file.endswith(".csv"):
                        file_path = os.path.join(root, file)
                        print(f"Restoring original timecode values at {file_path}")
                        process_csv(file_path, True)
            os.remove(os.path.join(SUBTITLE_FOLDER, "subtitle.fix"))

    answer = input("Do you want to compile ASSETS.DAT? (Y/N) ").strip().lower()
    if answer == "y":        
        compile_assets()

if __name__ == "__main__":
    main()
