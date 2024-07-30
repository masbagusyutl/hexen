import requests
import time
import json
from datetime import datetime, timedelta
from colorama import Fore, Style

# File path
data_file = 'data.txt'

# URLs
login_url = 'https://clicker.hexn.cc/v1/state'
booster_url = 'https://clicker.hexn.cc/v1/apply-farming-booster'
claim_url = 'https://clicker.hexn.cc/v1/farming/start'

def load_accounts(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def login(account_data):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Content-Length': '374',  # Panjang payload aktual bisa dihitung secara dinamis
        'Fingerprint': '7b5f8282144087cf265aaab3282600b5',
        'Origin': 'https://tgapp.hexn.cc',
        'Platform': 'WEB',
        'Platform-Version': '0.0.42',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Trace-Uuid': '3d2c7ff6-e2db-42fb-9848-877ea0722960',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    payload = {
        'init_data': account_data
    }
    response = requests.post(login_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        balance = data['data']['balance']
        username = json.loads(account_data)['username']
        print(f"{Fore.GREEN}Login successful for account {username}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Balance: {balance}{Style.RESET_ALL}")
        return data
    else:
        print(f"{Fore.RED}Login failed for account {account_data}{Style.RESET_ALL}")
        return None

def claim_booster(account_data):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Content-Length': '374',  # Panjang payload aktual bisa dihitung secara dinamis
        'Fingerprint': '7b5f8282144087cf265aaab3282600b5',
        'Origin': 'https://tgapp.hexn.cc',
        'Platform': 'WEB',
        'Platform-Version': '0.0.42',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Trace-Uuid': '3d2c7ff6-e2db-42fb-9848-877ea0722960',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    payload = {
        'init_data': account_data
    }
    response = requests.post(booster_url, headers=headers)
    if response.status_code == 200:
        print(f"{Fore.GREEN}Booster claimed successfully for account {account_data}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Failed to claim booster for account {account_data}{Style.RESET_ALL}")

def claim_8_hours(account_data):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Content-Length': '374',  # Panjang payload aktual bisa dihitung secara dinamis
        'Fingerprint': '7b5f8282144087cf265aaab3282600b5',
        'Origin': 'https://tgapp.hexn.cc',
        'Platform': 'WEB',
        'Platform-Version': '0.0.42',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Trace-Uuid': '3d2c7ff6-e2db-42fb-9848-877ea0722960',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    payload = {
        'init_data': account_data
    }
    response = requests.post(claim_url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        points = data['data']['points_amount']
        print(f"{Fore.GREEN}8-hour claim successful for account {account_data}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Points claimed: {points}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Failed to claim 8-hour task for account {account_data}{Style.RESET_ALL}")

def countdown_timer(duration):
    end_time = datetime.now() + timedelta(seconds=duration)
    while True:
        remaining = end_time - datetime.now()
        if remaining.total_seconds() <= 0:
            break
        print(f"\rTime remaining: {remaining}", end='')
        time.sleep(1)
    print("\nTimer completed!")

def main():
    accounts = load_accounts(data_file)
    total_accounts = len(accounts)
    print(f"{Fore.CYAN}Total accounts: {total_accounts}{Style.RESET_ALL}")

    while True:
        for index, account_data in enumerate(accounts):
            print(f"{Fore.CYAN}Processing account {index + 1}/{total_accounts}{Style.RESET_ALL}")
            
            login_response = login(account_data)
            if login_response:
                claim_booster(account_data)
                claim_8_hours(account_data)
            
            print(f"{Fore.CYAN}Waiting 5 seconds before processing the next account...{Style.RESET_ALL}")
            time.sleep(5)

        print(f"{Fore.CYAN}All accounts processed. Starting 8-hour countdown...{Style.RESET_ALL}")
        countdown_timer(28800)  # 8 hours in seconds

if __name__ == "__main__":
    main()
