import requests
import time
from datetime import datetime, timedelta

def load_access_tokens():
    try:
        with open('data.txt', 'r') as file:
            lines = file.readlines()
            access_tokens = [line.strip() for line in lines if line.startswith('eyJ0')]
            return access_tokens
    except FileNotFoundError:
        print("File data.txt not found.")
        return []

def perform_claim_request(access_token):
    url = 'https://api.hexn.cc/v1/kyc/marketing/farming/claim/'
    headers = {
        'Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers)
    return response

def perform_start_farming_request(access_token):
    url = 'https://api.hexn.cc/v1/kyc/marketing/farming/start/'
    headers = {
        'Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers)
    return response

def countdown_timer(seconds):
    while seconds:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        time_left = "{:02d}:{:02d}:{:02d}".format(h, m, s)
        print(f"Countdown: {time_left} remaining", end="\r")
        time.sleep(1)
        seconds -= 1

def main():
    while True:
        access_tokens = load_access_tokens()
        num_accounts = len(access_tokens)
        current_account_index = 0

        print(f"Total accounts in data.txt: {num_accounts}")

        if num_accounts == 0:
            print("No accounts found in data.txt. Exiting program.")
            return

        for access_token in access_tokens:
            current_account_index += 1
            print(f"Processing account {current_account_index} of {num_accounts}")
            
            # Perform claim request
            claim_response = perform_claim_request(access_token)
            
            if claim_response.status_code == 200:
                print("Claim request successful.")
            else:
                print(f"Claim request failed with status code {claim_response.status_code}.")
            
            # Perform farming start request
            start_response = perform_start_farming_request(access_token)
            
            if start_response.status_code == 200:
                print("Farming start request successful.")
            else:
                print(f"Farming start request failed with status code {start_response.status_code}.")
            
            # Pause for 5 seconds before processing the next account
            if current_account_index < num_accounts:
                print("Waiting for 5 seconds before the next account...")
                time.sleep(5)

        # After processing all accounts, start 8-hour countdown
        print("All accounts processed. Starting 8-hour countdown now.")

        countdown_seconds = 8 * 60 * 60  # 8 hours in seconds
        end_time = datetime.now() + timedelta(seconds=countdown_seconds)
        while datetime.now() < end_time:
            time_remaining = int((end_time - datetime.now()).total_seconds())
            countdown_timer(time_remaining)
            time.sleep(1)
        print("\nCountdown completed. Restarting process.")

if __name__ == "__main__":
    main()
