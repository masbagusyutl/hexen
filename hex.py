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

def process_accounts():
    global last_booster_claim
    accounts = read_accounts()
    num_accounts = len(accounts)
    print(f"Jumlah akun: {num_accounts}")

    while True:
        for idx, init_data in enumerate(accounts):
            print(f"\nMemproses akun {idx + 1}/{num_accounts}")
            
            # Login
            print("Login...")
            login_response = login(init_data)
            if "data" in login_response:
                balance = login_response["data"].get("balance", "Tidak tersedia")
                print(f"Balance akun: {balance}")

                farming_data = login_response["data"].get("farming", {})
                if farming_data:
                    start_at = format_timestamp(farming_data.get("start_at", 0))
                    end_at = format_timestamp(farming_data.get("end_at", 0))
                    points_amount = farming_data.get("points_amount", "Tidak tersedia")
                    print(f"Farming mulai pada: {start_at}")
                    print(f"Bisa farming lagi pada: {end_at}")
                    print(f"Poin yang akan didapatkan: {points_amount}")
                    
                    # Simpan waktu mulai farming berikutnya
                    next_farming_time[init_data] = datetime.fromtimestamp(farming_data.get("end_at", 0) / 1000)

                    now = datetime.now()
                    if now < next_farming_time[init_data]:
                        print("Belum waktunya farming.")
                    else:
                        print("Waktunya farming. Memulai tugas farming...")
                        farming_claim_response = farming_claim(init_data)
                        if "data" in farming_claim_response:
                            points_amount = farming_claim_response["data"].get("points_amount", "Tidak tersedia")
                            start_at = format_timestamp(farming_claim_response["data"].get("start_at", 0))
                            end_at = format_timestamp(farming_claim_response["data"].get("end_at", 0))
                            print(f"Poin yang didapat dari farming: {points_amount}")
                            print(f"Farming mulai pada: {start_at}")
                            print(f"Bisa farming lagi pada: {end_at}")
                        else:
                            error_message = farming_claim_response.get("message", "Terjadi kesalahan saat klaim farming.")
                            print(f"{error_message}")

                # Menyelesaikan Tugas Quest
                quests = login_response["data"].get("quests", {})
                for quest_id, quest in quests.items():
                    quest_description = quest.get("description")
                    quest_points = quest.get("points_amount")
                    print(f"Menyelesaikan tugas: {quest_description} (ID: {quest_id})")
                    quest_response = execute_quest(init_data, quest_id)
                    if "data" in quest_response:
                        print(f"Tugas selesai: {quest_description}")
                        print(f"Poin yang didapat: {quest_points}")
                    else:
                        error_message = quest_response.get("message", "Terjadi kesalahan saat menyelesaikan tugas.")
                        print(f"{error_message}")
                    time.sleep(2)

                # Klaim Booster (hanya 1 hari sekali)
                farming_boosters = login_response["data"].get("farming_boosters", {})
                if farming_boosters:
                    for booster_id, booster in farming_boosters.items():
                        booster_description = booster.get("description")
                        booster_time = booster.get("time_after_parent_booster")

                        now = datetime.now()
                        if now - last_booster_claim >= timedelta(days=1):
                            print("Mengklaim booster...")
                            booster_response = claim_booster(init_data, booster_id)
                            if "data" in booster_response:
                                print(f"Booster telah diklaim: {booster_description}")
                                print(f"Booster berlaku selama: {booster_time}")
                                last_booster_claim = now
                            else:
                                error_message = booster_response.get("message", "Terjadi kesalahan saat klaim booster.")
                                print(f"{error_message}")
                            break
                        else:
                            print("Booster sudah diklaim hari ini.")
                            break
                else:
                    print("Tidak ada data booster tersedia.")
                
                # Klaim 8 Jam
                print("Mengklaim 8 jam...")
                claim_response = claim_8_hours(init_data)
                if "data" in claim_response:
                    points_amount = claim_response["data"].get("points_amount", "Tidak tersedia")
                    if points_amount == "Tidak tersedia":
                        print("Belum waktunya mengklaim 8 jam untuk akun ini.")
                    else:
                        print(f"Poin yang didapat: {points_amount}")
                else:
                    error_message = claim_response.get("message", "Terjadi kesalahan saat klaim 8 jam.")
                    print(f"{error_message}")
                
            else:
                print("Login gagal atau data tidak tersedia.")
                continue

            # Jeda 5 detik antar akun
            time.sleep(5)
        
        # Hitung mundur hingga waktu farming berikutnya
        if next_farming_time:
            next_time = min(next_farming_time.values())
            now = datetime.now()
            seconds_until_next_farming = (next_time - now).total_seconds()
            print(f"\nHitung mundur hingga tugas farming berikutnya: {seconds_until_next_farming / 3600:.2f} jam")
            countdown_timer(int(seconds_until_next_farming))

if __name__ == "__main__":
    process_accounts()
