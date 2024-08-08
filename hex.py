import requests
import time
import sys
from datetime import datetime, timedelta

# Konstanta
LOGIN_URL = "https://clicker.hexn.cc/v1/state"
CLAIM_URL = "https://clicker.hexn.cc/v1/farming/start"
FARMING_CLAIM_URL = "https://clicker.hexn.io/v1/farming/claim"
DATA_FILE = "data.txt"
ERROR_LOG_FILE = "error_log.txt"

# Variabel global untuk menyimpan waktu farming berikutnya
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

def log_error(task, error_message, response):
    with open(ERROR_LOG_FILE, "a") as file:
        file.write(f"Error pada {task}: {error_message}\n")
        file.write(f"Respon: {response}\n\n")

def process_accounts():
    while True:
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
                            print("Mengklaim Farming...")
                            claim_response = claim_8_hours(init_data)
                            if "data" in claim_response:
                                points_amount = claim_response["data"].get("points_amount", "Tidak tersedia")
                                start_at = format_timestamp(claim_response["data"].get("start_at", 0))
                                end_at = format_timestamp(claim_response["data"].get("end_at", 0))
                                print(f"Poin yang didapat dari farming: {points_amount}")
                                print(f"Farming mulai pada: {start_at}")
                                print(f"Bisa farming lagi pada: {end_at}")
                            else:
                                error_message = claim_response.get("message", "Terjadi kesalahan saat klaim farming.")
                                print(f"{error_message}")
                                log_error("claim_8_hours", error_message, claim_response)
                        else:
                            error_message = farming_claim_response.get("message", "Terjadi kesalahan saat klaim farming.")
                            print(f"{error_message}")
                            log_error("farming_claim", error_message, farming_claim_response)
                    else:
                        print("Belum waktunya farming.")
                else:
                    print("Tidak ada data farming yang tersedia.")
            else:
                error_message = login_response.get("message", "Terjadi kesalahan saat login.")
                print(f"{error_message}")
                log_error("login", error_message, login_response)
            
            # Tunggu 5 detik sebelum memproses akun berikutnya
            time.sleep(5)

        # Menunggu hingga waktu farming berikutnya
        if next_farming_time:
            next_time = min(next_farming_time.values())
            now = datetime.now()
            seconds_until_next_farming = (next_time - now).total_seconds()
            if seconds_until_next_farming > 0:
                print(f"Menunggu hingga {format_timestamp(next_time.timestamp() * 1000)}")
                countdown_timer(int(seconds_until_next_farming))

if __name__ == "__main__":
    process_accounts()
