import requests
import time
import sys
from datetime import datetime, timedelta

# Konstanta
LOGIN_URL = "https://clicker.hexn.cc/v1/state"
BOOSTER_URL = "https://clicker.hexn.cc/v1/apply-farming-booster"
CLAIM_URL = "https://clicker.hexn.cc/v1/farming/start"
FARMING_CLAIM_URL = "https://clicker.hexn.io/v1/farming/claim"
QUEST_URL = "https://clicker.hexn.io/v1/executed-quest/start"
DATA_FILE = "data.txt"

# Variabel global untuk menyimpan waktu terakhir klaim booster
last_booster_claim = datetime.now() - timedelta(days=1)
next_farming_time = {}

def read_accounts():
    with open(DATA_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]

def login(init_data):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"init_data": init_data}
    response = requests.post(LOGIN_URL, headers=headers, json=payload)
    return response.json()

def claim_booster(init_data, booster_id):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"init_data": init_data, "booster_id": booster_id}
    response = requests.post(BOOSTER_URL, headers=headers, json=payload)
    return response.json()

def claim_8_hours(init_data):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"init_data": init_data}
    response = requests.post(CLAIM_URL, headers=headers, json=payload)
    return response.json()

def farming_claim(init_data):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"init_data": init_data}
    response = requests.post(FARMING_CLAIM_URL, headers=headers, json=payload)
    return response.json()

def execute_quest(init_data, quest_id):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"init_data": init_data, "quest_id": quest_id}
    response = requests.post(QUEST_URL, headers=headers, json=payload)
    return response.json()

def countdown_timer(seconds):
    start_time = time.time()
    while seconds:
        elapsed = time.time() - start_time
        remaining = seconds - int(elapsed)
        if remaining < 0:
            break
        mins, secs = divmod(remaining, 60)
        hours, mins = divmod(mins, 60)
        sys.stdout.write(f"\rWaktu tersisa: {hours:02}:{mins:02}:{secs:02}")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n")

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

def get_next_booster_id(applied_boosters, farming_boosters):
    # Mendapatkan ID booster terakhir yang diterapkan
    if not applied_boosters:
        return min(farming_boosters.keys())  # Mengembalikan ID booster pertama jika belum ada booster yang diterapkan

    last_booster_id = max(applied_boosters.keys(), key=lambda k: applied_boosters[k])
    farming_boosters_sorted = sorted(farming_boosters.keys(), key=int)
    
    try:
        next_booster_id = farming_boosters_sorted[farming_boosters_sorted.index(last_booster_id) + 1]
    except IndexError:
        next_booster_id = farming_boosters_sorted[0]  # Reset ke ID booster pertama jika tidak ada booster berikutnya

    return next_booster_id

def process_accounts():
    global last_booster_claim
    while True:  # Loop utama agar script mengulang terus-menerus
        accounts = read_accounts()
        num_accounts = len(accounts)
        print(f"Jumlah akun: {num_accounts}")

        for idx, init_data in enumerate(accounts):
            print(f"\nMemproses akun {idx + 1}/{num_accounts}")
            
            # Login
            print("Login...")
            login_response = login(init_data)
            if "data" in login_response:
                balance = login_response["data"].get("balance", "Tidak tersedia")
                print(f"Balance akun: {balance}")

                config = login_response["data"].get("config", {})
                if config:
                    farming_boosters = config.get("farming_boosters", {})
                    quests = config.get("quests", {})
                    applied_boosters = login_response["data"].get("applied_boosters", {})

                    # Klaim Booster (hanya 1 hari sekali)
                    if farming_boosters:
                        now = datetime.now()
                        if now - last_booster_claim >= timedelta(days=1):
                            next_booster_id = get_next_booster_id(applied_boosters, farming_boosters)
                            booster_description = farming_boosters[next_booster_id].get("description")
                            booster_time = farming_boosters[next_booster_id].get("time_after_parent_booster")

                            print("Mengklaim booster...")
                            booster_response = claim_booster(init_data, next_booster_id)
                            if "data" in booster_response:
                                print(f"Booster telah diklaim: {booster_description}")
                                print(f"Booster berlaku selama: {booster_time}")
                                last_booster_claim = now
                            else:
                                error_message = booster_response.get("message", "Terjadi kesalahan saat klaim booster.")
                                print(f"{error_message}")
                        else:
                            print("Booster sudah diklaim hari ini.")
                    else:
                        print("Tidak ada data booster tersedia.")

                    # Menyelesaikan Tugas Quest
                    if quests:
                        total_completed = 0
                        for quest_id, quest in quests.items():
                            quest_description = quest.get("description")
                            quest_points = quest.get("points_amount")
                            print(f"Menyelesaikan tugas: {quest_description} (ID: {quest_id})")
                            quest_response = execute_quest(init_data, quest_id)
                            if "data" in quest_response:
                                print(f"Tugas selesai: {quest_description}")
                                print(f"Poin yang didapat: {quest_points}")
                                total_completed += 1
                            else:
                                error_message = quest_response.get("message", "Terjadi kesalahan saat menyelesaikan tugas.")
                                print(f"{error_message}")
                            time.sleep(2)
                        
                        print(f"Jumlah tugas yang diselesaikan: {total_completed}")
                    else:
                        print("Tidak ada data quest tersedia.")
                
                else:
                    print("Login gagal atau data tidak tersedia.")
                    continue

            # Jeda 5 detik antar akun
            time.sleep(5)

        # Ambil waktu farming berikutnya yang paling lama di antara semua akun
        if next_farming_time:
            next_time = max(next_farming_time.values())
            now = datetime.now()
            seconds_until_next_farming = (next_time - now).total_seconds()
            print(f"\nHitung mundur hingga tugas farming berikutnya: {seconds_until_next_farming / 3600:.2f} jam")
            countdown_timer(int(seconds_until_next_farming))

if __name__ == "__main__":
    process_accounts()
