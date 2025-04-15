import os
import time
import random
import re
from datetime import datetime, timedelta

# Constants
REGISTRATION_DURATION = 3600  # 1 hour in seconds
EXTENSION_DURATION = 1800     # 30 minutes in seconds
MIN_USERS = 5
LOG_FILE = "lottery_log.txt"
TIMER_FILE = "timer_state.txt"
AUTOSAVE_INTERVAL = 2         # 2 seconds

# Global variables
registered_users = set()
start_time = datetime.now()
last_autosave_time = start_time

# Load end_time from file if available
if os.path.exists(TIMER_FILE):
    with open(TIMER_FILE, "r") as f:
        saved_time = f.read().strip()
        try:
            end_time = datetime.fromisoformat(saved_time)
        except ValueError:
            end_time = start_time + timedelta(seconds=REGISTRATION_DURATION)
else:
    end_time = start_time + timedelta(seconds=REGISTRATION_DURATION)

# Load previously registered users
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as file:
        for line in file:
            if line.strip() and not line.startswith("Winner:") and not line.startswith("No winner"):
                registered_users.add(line.strip())

def save_end_time():
    with open(TIMER_FILE, "w") as f:
        f.write(end_time.isoformat())

def is_valid_username(username):
    return bool(re.match("^[a-zA-Z0-9]+$", username))

def autosave_users():
    global last_autosave_time
    with open(LOG_FILE, "w") as file:
        for user in registered_users:
            file.write(f"{user}\n")
    last_autosave_time = datetime.now()

def display_status():
    remaining_time = (end_time - datetime.now()).total_seconds()
    if remaining_time > 0:
        print(f"\nRemaining registration time: {int(remaining_time // 60)} minutes {int(remaining_time % 60)} seconds")
    print(f"Registered users: {len(registered_users)}")

def register_user():
    global end_time
    while datetime.now() < end_time:
        username = input("Enter a username (alphanumeric only): ").strip()
        if not username:
            print("Username cannot be empty. Please try again.")
        elif not is_valid_username(username):
            print("Username can only contain letters and numbers. Please try again.")
        elif username in registered_users:
            print("Username already exists. Please try again.")
        else:
            registered_users.add(username)
            print(f"User '{username}' registered successfully.")
            if (datetime.now() - last_autosave_time).total_seconds() >= AUTOSAVE_INTERVAL:
                autosave_users()
            save_end_time()
            break

def pick_winner():
    global end_time, registered_users
    if len(registered_users) >= MIN_USERS:
        winner = random.choice(list(registered_users))
        print(f"\n🎉 The winner is: {winner} 🎉")
        print(f"Total participants: {len(registered_users)}")
        with open(LOG_FILE, "a") as file:
            file.write(f"Winner: {winner}\n")
        if os.path.exists(TIMER_FILE):
            os.remove(TIMER_FILE)

        # Clear users after winner is announced
        registered_users.clear()
        autosave_users()
        print("✅ All participants have been reset.")

        # Optionally restart the registration for next round
        restart_lottery()

    else:
        print("\n❌ Not enough users registered. Extending registration by 30 minutes.")
        end_time += timedelta(seconds=EXTENSION_DURATION)
        save_end_time()
        while datetime.now() < end_time:
            display_status()
            register_user()
        if len(registered_users) >= MIN_USERS:
            pick_winner()
        else:
            print("\nStill not enough users registered. Exiting the program.")
            with open(LOG_FILE, "a") as file:
                file.write("No winner selected due to insufficient participants.\n")

def restart_lottery():
    global start_time, end_time, last_autosave_time
    print("\n🔁 Starting new lottery round...")
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=REGISTRATION_DURATION)
    last_autosave_time = start_time
    save_end_time()
    run_lottery()

def run_lottery():
    print(f"Registration ends at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    while datetime.now() < end_time:
        display_status()
        register_user()
    print("\n⏰ Registration time has ended!")
    autosave_users()
    pick_winner()

# Main program
try:
    print("Welcome to the Lottery Registration System!")
    run_lottery()
except KeyboardInterrupt:
    print("\nProgram interrupted. Autosaving current registrations and time...")
    autosave_users()
    save_end_time()
    print("Exiting the program.")
