import requests
import time
import json
import sys
from datetime import datetime, timedelta

# Konstanta
LOGIN_URL = "https://clicker.hexn.cc/v1/state"
BOOSTER_URL = "https://clicker.hexn.cc/v1/apply-farming-booster"
CLAIM_URL = "https://clicker.hexn.cc/v1/farming/start"
DATA_FILE = "data.txt"

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

def claim_booster(init_data):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"init_data": init_data}
    response = requests.post(BOOSTER_URL, headers=headers, json=payload)
    return response.json()

def claim_8_hours(init_data):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"init_data": init_data}
    response = requests.post(CLAIM_URL, headers=headers, json=payload)
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

def process_accounts():
    accounts = read_accounts()
    num_accounts = len(accounts)
    print(f"Jumlah akun: {num_accounts}")

    while True:
        for idx, init_data in enumerate(accounts):
            print(f"\nMemproses akun {idx + 1}/{num_accounts}")
            
            # Login
            print("Login...")
            login_response = login(init_data)
            balance = login_response["data"]["balance"]
            print(f"Balance akun: {balance}")
            
            # Claim Booster
            print("Mengklaim booster...")
            booster_response = claim_booster(init_data)
            print("Booster telah diklaim.")
            
            # Claim 8 Hours
            print("Mengklaim 8 jam...")
            claim_response = claim_8_hours(init_data)
            points_amount = claim_response["data"].get("points_amount", "Tidak tersedia")
            print(f"Poin yang didapat: {points_amount}")

            # Jeda 5 detik antar akun
            time.sleep(5)
        
        # Hitung mundur 8 jam
        print("\nHitung mundur 8 jam dimulai...")
        countdown_timer(28800)  # 8 hours in seconds

if __name__ == "__main__":
    process_accounts()
