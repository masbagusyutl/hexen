import time
import requests
import json
from datetime import datetime, timedelta

def parse_account(line):
    account = {}
    pairs = line.strip().split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            account[key] = value
    return account

def load_accounts(file_path='data.txt'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    accounts = [parse_account(line) for line in lines]
    return accounts

def make_post_request(url, headers, payload=None):
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request to {url} failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred during the request to {url}: {e}")
        return None

def login(account):
    url = 'https://clicker.hexn.cc/v1/state'
    headers = {'Content-Type': 'application/json'}
    
    response = make_post_request(url, headers, account)
    
    if response:
        user_info = json.loads(account['user'])
        username = user_info['username']
        balance = response['data']['balance']
        print(f"Account: {username}, Balance: {balance}")
        return True, username, balance
    else:
        print("Login failed.")
        return False, None, None

def claim_booster(account):
    url = 'https://clicker.hexn.cc/v1/booster'
    headers = {'Content-Type': 'application/json'}
    
    response = make_post_request(url, headers, account)
    
    if response:
        print(f"Booster claimed successfully for account.")
        return True
    else:
        print("Booster claim failed.")
        return False

def claim_8_hour_points(account):
    url = 'https://clicker.hexn.cc/v1/8hourpoints'
    headers = {'Content-Type': 'application/json'}
    
    response = make_post_request(url, headers, account)
    
    if response:
        print(f"8-hour points claimed successfully for account.")
        return True
    else:
        print("8-hour points claim failed.")
        return False

def countdown_timer(hours):
    end_time = datetime.now() + timedelta(hours=hours)
    while datetime.now() < end_time:
        time_left = end_time - datetime.now()
        print(f"Time left: {str(time_left).split('.')[0]}", end='\r')
        time.sleep(1)
    print("\nCountdown finished. Restarting tasks...")

def main():
    accounts = load_accounts()
    num_accounts = len(accounts)
    print(f"Total accounts: {num_accounts}")

    while True:
        for i, account in enumerate(accounts, 1):
            print(f"Processing account {i}/{num_accounts}")
            
            success, username, balance = login(account)
            if success:
                if claim_booster(account):
                    print(f"Booster claimed successfully for account {username}.")
                else:
                    print(f"Booster claim failed for account {username}.")
                    
                if claim_8_hour_points(account):
                    print(f"8-hour points claimed successfully for account {username}.")
                else:
                    print(f"8-hour points claim failed for account {username}.")
            else:
                print(f"Skipping account {i} due to login failure.")
            
            print(f"Waiting 5 seconds before processing next account...")
            time.sleep(5)
        
        print("All accounts processed. Starting 8-hour countdown.")
        countdown_timer(8)

if __name__ == "__main__":
    main()
