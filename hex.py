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
                farming_boosters = login_response["data"].get("config", {}).get("farming_boosters", {})

                if applied_boosters:
                    last_booster_id = max(applied_boosters, key=lambda k: applied_boosters[k])
                    last_booster_time = datetime.fromtimestamp(applied_boosters[last_booster_id] / 1000)
                    days_since_last_booster = (datetime.now() - last_booster_time).days

                    booster_ids = list(farming_boosters.keys())
                    if days_since_last_booster < len(booster_ids):
                        next_booster_id = booster_ids[days_since_last_booster]
                        booster = farming_boosters.get(next_booster_id, {})
                        booster_description = booster.get("description", "Deskripsi tidak tersedia")
                        booster_time = booster.get("time_after_parent_booster", "Durasi tidak tersedia")

                        print(f"Booster yang terakhir diklaim: ID {last_booster_id} pada hari ke-{days_since_last_booster}")
                        print(f"Mengklaim booster hari ke-{days_since_last_booster + 1} dengan ID {next_booster_id}...")
                        if datetime.now() - last_booster_claim >= timedelta(days=1):
                            booster_response = claim_booster(init_data, next_booster_id)
                            if "data" in booster_response:
                                print(f"Booster telah diklaim: {booster_description}")
                                print(f"Booster berlaku selama: {booster_time}")
                                last_booster_claim = datetime.now()
                            else:
                                error_message = booster_response.get("message", "Terjadi kesalahan saat klaim booster.")
                                print(f"{error_message}")
                        else:
                            print("Booster sudah diklaim hari ini.")
                    else:
                        print("Semua booster sudah diklaim hari ini.")
                else:
                    print("Tidak ada data booster tersedia. Mulai klaim booster dari ID 1 (hari ke-1).")
                    if datetime.now() - last_booster_claim >= timedelta(days=1):
                        next_booster_id = "1"
                        booster = farming_boosters.get(next_booster_id, {})
                        booster_description = booster.get("description", "Deskripsi tidak tersedia")
                        booster_time = booster.get("time_after_parent_booster", "Durasi tidak tersedia")

                        print(f"Mengklaim booster hari ke-1 dengan ID {next_booster_id}...")
                        booster_response = claim_booster(init_data, next_booster_id)
                        if "data" in booster_response:
                            print(f"Booster telah diklaim: {booster_description}")
                            print(f"Booster berlaku selama: {booster_time}")
                            last_booster_claim = datetime.now()
                        else:
                            error_message = booster_response.get("message", "Terjadi kesalahan saat klaim booster.")
                            print(f"{error_message}")
                    else:
                        print("Booster sudah diklaim hari ini.")

                # Menyelesaikan Tugas Quest
                executed_quests = login_response["data"].get("executed_quests", {})
                quests = login_response["data"].get("config", {}).get("quests", {})
                completed_quests_count = 0

                if quests:
                    for quest_id, quest in quests.items():
                        if executed_quests.get(quest_id, False):
                            completed_quests_count += 1
                            continue

                        quest_description = quest.get("description", "Deskripsi tidak tersedia")
                        quest_points = quest.get("points_amount", "Tidak tersedia")
                        print(f"Menyelesaikan tugas: {quest_description} (ID: {quest_id})")
                        quest_response = execute_quest(init_data, quest_id)
                        if "data" in quest_response:
                            print(f"Tugas selesai: {quest_description}")
                            print(f"Poin yang didapat: {quest_points}")
                        else:
                            error_message = quest_response.get("message", "Terjadi kesalahan saat menyelesaikan tugas.")
                            print(f"{error_message}")
                        time.sleep(2)

                print(f"Jumlah tugas yang telah diselesaikan: {completed_quests_count}")

            else:
                print(f"Login gagal untuk akun {idx + 1}. Mengabaikan akun ini.")

            time.sleep(5)  # Jeda 5 detik antar akun

        # Menunggu hingga waktu farming berikutnya
        if next_farming_time:
            next_time = min(next_farming_time.values())
            now = datetime.now()
            seconds_until_next_farming = (next_time - now).total_seconds()
            if seconds_until_next_farming > 0:
                print(f"Menunggu hingga {format_timestamp(next_time.timestamp() * 1000)}")
                countdown_timer(int(seconds_until_next_farming))

# Memulai proses
if __name__ == "__main__":
    process_accounts()
