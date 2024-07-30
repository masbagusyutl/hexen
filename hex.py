import requests
import time
import json
from datetime import datetime, timedelta

def read_accounts(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def extract_username(init_data):
    # Extract username from initData
    start = init_data.find('username%22%3A%22') + len('username%22%3A%22')
    end = init_data.find('%22', start)
    return init_data[start:end]

def make_post_request(url, headers, payload=None):
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def login(init_data):
    url = "https://clicker.hexn.cc/v1/state"
    headers = {"Initdata": init_data}
    response = make_post_request(url, headers)
    if response["status"] == "OK":
        username = extract_username(init_data)
        balance = response["data"]["balance"]
        print(f"Login successful for {username}. Balance: {balance}")
        return username, balance
    else:
        print(f"Login failed for init_data: {init_data}")
        return None, None

def claim_booster(init_data):
    url = "https://clicker.hexn.cc/v1/booster"
    headers = {"Initdata": init_data}
    response = make_post_request(url, headers)
    if response["status"] == "OK":
        print(f"Booster claimed successfully for init_data: {init_data}")
    else:
        print(f"Failed to claim booster for init_data: {init_data}")

def claim_8_hour_points(init_data):
    url = "https://clicker.hexn.cc/v1/claim"
    headers = {"Initdata": init_data}
    response = make_post_request(url, headers)
    if response["status"] == "OK":
        points_amount = response["data"]["points_amount"]
        print(f"8-hour points claimed successfully for init_data: {init_data}. Points: {points_amount}")
        return points_amount
    else:
        print(f"Failed to claim 8-hour points for init_data: {init_data}")
        return 0

def countdown(duration_seconds):
    end_time = datetime.now() + timedelta(seconds=duration_seconds)
    while datetime.now() < end_time:
        remaining_time = end_time - datetime.now()
        print(f"\rTime until next cycle: {remaining_time}", end='')
        time.sleep(1)
    print()

def main():
    accounts = read_accounts("data.txt")
    print(f"Total accounts: {len(accounts)}")
    
    while True:
        total_points = 0
        for i, init_data in enumerate(accounts):
            print(f"Processing account {i + 1} of {len(accounts)}")
            username, balance = login(init_data)
            if username:
                claim_booster(init_data)
                points = claim_8_hour_points(init_data)
                total_points += points
            time.sleep(5)  # Wait for 5 seconds before processing the next account

        print(f"Total points claimed: {total_points}")
        print("All accounts processed. Starting 8-hour countdown.")
        countdown(8 * 60 * 60)  # 8 hours countdown

if __name__ == "__main__":
    main()
