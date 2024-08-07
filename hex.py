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

def claim_booster(init_data, applied_boosters):
    headers = {
        "Content-Type": "application/json",
    }
    
    # Menentukan booster_id berikutnya yang akan diklaim
    now = datetime.now()
    booster_id_to_claim = None

    # Ambil booster_id terakhir yang diklaim
    if applied_boosters:
        last_booster_id = max(applied_boosters.keys(), key=int)
        last_booster_timestamp = applied_boosters[last_booster_id]
        last_booster_date = datetime.fromtimestamp(last_booster_timestamp / 1000)
        
        # Hitung jumlah hari sejak booster terakhir diklaim
        days_since_last_booster = (now - last_booster_date).days
        
        # Pilih booster_id berikutnya
        if days_since_last_booster >= 1:
            booster_id_to_claim = str((int(last_booster_id) % 9) + 1)
    
    if booster_id_to_claim:
        payload = {"init_data": init_data, "booster_id": booster_id_to_claim}
        response = requests.post(BOOSTER_URL, headers=headers, json=payload)
        return response.json()
    else:
        print("Tidak ada booster yang perlu diklaim saat ini.")
        return {}

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

def execute_quest(init_data, executed_quests):
    headers = {
        "Content-Type": "application/json",
    }
    
    quests_to_complete = {}
    total_completed = 0
    
    # Periksa tipe data dari executed_quests
    if isinstance(executed_quests, dict):
        for quest_id, quest_info in executed_quests.items():
            if isinstance(quest_info, dict):
                if not quest_info.get('completed', False):
                    quests_to_complete[quest_id] = quest_info
            elif isinstance(quest_info, bool):
                if not quest_info:
                    quests_to_complete[quest_id] = {"description": "Unknown", "points_amount": "Unknown"}
            else:
                print(f"Data format tidak dikenali untuk quest ID {quest_id}.")
    
    if quests_to_complete:
        for quest_id, quest_info in quests_to_complete.items():
            quest_description = quest_info.get("description", f"Tugas ID {quest_id}")
            print(f"Menyelesaikan tugas: {quest_description} (ID: {quest_id})")
            payload = {"init_data": init_data, "quest_id": quest_id}
            response = requests.post(QUEST_URL, headers=headers, json=payload)
            if "data" in response.json():
                print(f"Tugas selesai: {quest_description}")
                total_completed += 1
            else:
                error_message = response.json().get("message", "Terjadi kesalahan saat menyelesaikan tugas.")
                print(f"{error_message}")
            time.sleep(2)
        
        print(f"Jumlah tugas yang diselesaikan: {total_completed}")
    else:
        print("Tidak ada tugas quest yang perlu diselesaikan.")

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
                    if now >= next_farming_time[init_data]:
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

                        # Klaim 8 Jam setelah farming
                        print("Mengklaim Farming...")
                        claim_response = claim_8_hours(init_data)
                        if "data" in claim_response:
                            points_amount = claim_response["data"].get("points_amount", "Tidak tersedia")
                            if points_amount == "Tidak tersedia":
                                print("Belum waktunya farming untuk akun ini.")
                            else:
                                print(f"Poin yang didapat: {points_amount}")
                        else:
                            error_message = claim_response.get("message", "Terjadi kesalahan saat klaim farming.")
                            print(f"{error_message}")

                    else:
                        print("Belum waktunya farming. Coba klaim booster atau jalankan tugas quest.")
                else:
                    print("Tidak ada data farming yang tersedia.")

                # Klaim Booster (hanya 1 hari sekali)
                applied_boosters = login_response["data"].get("applied_boosters", {})
                print("Mengklaim booster...")
                booster_response = claim_booster(init_data, applied_boosters)
                if "data" in booster_response:
                    print(f"Booster telah diklaim.")
                else:
                    error_message = booster_response.get("message", "Terjadi kesalahan saat klaim booster.")
                    print(f"{error_message}")

                # Menyelesaikan Tugas Quest
                executed_quests = login_response["data"].get("executed_quests", {})
                print("Menyelesaikan tugas quest...")
                execute_quest(init_data, executed_quests)
                
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
