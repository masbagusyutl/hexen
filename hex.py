import requests
import json
import time

def load_accounts():
    with open('data.txt', 'r') as file:
        lines = file.read().strip().split('\n')
    accounts = [parse_account(line) for line in lines if line]
    return accounts

def parse_account(account_str):
    pairs = account_str.split('&')
    account_data = {}
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            account_data[key] = value
    return account_data

def make_post_request(url, headers, payload=None):
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return None

def login(account):
    url = "https://clicker.hexn.cc/v1/login"  # Ganti dengan URL login yang benar
    headers = {
        "Initdata": account["query_id"],
    }
    response = make_post_request(url, headers)
    if response and response.get("code") == 200:
        username = json.loads(account["user"])["username"]
        balance = response["data"]["balance"]
        return True, username, balance
    return False, None, None

def claim_8_hours(account):
    url = "https://clicker.hexn.cc/v1/farming/start"
    headers = {
        "Authorization": account["hash"],
    }
    response = make_post_request(url, headers)
    if response and response.get("code") == 200:
        return response["data"]["pointClaimed"]
    return None

def apply_farming_booster(account):
    url = "https://clicker.hexn.cc/v1/apply-farming-booster"
    headers = {
        "Authorization": account["hash"],
    }
    response = make_post_request(url, headers)
    if response and response.get("code") == 200:
        return response["data"]["boosterApplied"]
    return None

def main():
    accounts = load_accounts()
    for idx, account in enumerate(accounts, start=1):
        print(f"Processing account {idx}/{len(accounts)}...")
        success, username, balance = login(account)
        if success:
            print(f"Logged in as {username}, balance: {balance}")
            booster_applied = apply_farming_booster(account)
            if booster_applied:
                print(f"Booster applied successfully for {username}.")
            else:
                print(f"Failed to apply booster for {username}.")

            time.sleep(5)  # Jeda 5 detik antar tugas

            point_claimed = claim_8_hours(account)
            if point_claimed:
                print(f"8-hour claim successful for {username}, points claimed: {point_claimed}")
            else:
                print(f"8-hour claim failed for {username}.")
        else:
            print(f"Login failed for account {idx}.")

        time.sleep(10)  # Jeda 10 detik antar akun

    print("All tasks completed.")

if __name__ == "__main__":
    main()
