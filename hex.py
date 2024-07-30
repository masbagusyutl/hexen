import requests
import time
import json
from datetime import datetime, timedelta

def read_accounts(filename='data.txt'):
    accounts = []
    usernames = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split('&')
            if len(parts) < 2:
                print(f"Skipping invalid line: {line.strip()}")
                continue  # Skip lines that don't have at least two parts
            account_data = parts[0]  # Assuming the first part contains the init_data
            username = extract_username(parts[1])  # Extract username from the second part
            accounts.append(account_data)
            usernames.append(username)
    return accounts, usernames

def extract_username(query_string):
    # Extract username from the query string
    username_key = 'username%22%3A%22'
    start = query_string.find(username_key) + len(username_key)
    end = query_string.find('%22', start)
    if start == -1 or end == -1:
        return 'Unknown'  # Return a default value if username is not found
    return query_string[start:end]

def login(account):
    url = 'https://clicker.hexn.cc/v1/state'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {
        'init_data': account
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def claim_booster(account):
    url = 'https://clicker.hexn.cc/v1/apply-farming-booster'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {
        'init_data': account
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def claim_8_hour(account):
    url = 'https://clicker.hexn.cc/v1/farming/start'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {
        'init_data': account
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def countdown_8_hours():
    end_time = datetime.now() + timedelta(hours=8)
    while True:
        remaining_time = end_time - datetime.now()
        if remaining_time.total_seconds() <= 0:
            break
        print(f'Next run in: {remaining_time}', end='\r')
        time.sleep(1)

def main():
    accounts, usernames = read_accounts()
    num_accounts = len(accounts)
    print(f'Number of accounts: {num_accounts}')
    
    while True:
        for idx, (account, username) in enumerate(zip(accounts, usernames)):
            print(f'\nProcessing account {idx + 1}/{num_accounts}')
            
            # Step 1: Login
            print('Logging in...')
            login_response = login(account)
            if login_response.get('status') == 'OK':
                balance = login_response['data']['balance']
                print(f'Account: {username}')
                print(f'Balance: {balance}')
            else:
                print('Login failed.')
                continue
            
            # Step 2: Claim booster
            print('Claiming booster...')
            booster_response = claim_booster(account)
            print(f'Booster claim response: {booster_response}')
            
            # Step 3: Claim 8 hour
            print('Claiming 8 hour...')
            claim_response = claim_8_hour(account)
            points_amount = claim_response.get('points_amount', 'N/A')
            print(f'Points claimed: {points_amount}')
            
            # Wait 5 seconds before processing next account
            print('Waiting 5 seconds before next account...')
            time.sleep(5)
        
        # Step 4: Countdown before restart
        print('All accounts processed. Starting countdown for next run.')
        countdown_8_hours()

if __name__ == '__main__':
    main()
