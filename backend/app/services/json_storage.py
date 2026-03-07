import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

DATA_FOLDER = os.path.join(BASE_DIR, "data")

RIDES_FILE = os.path.join(DATA_FOLDER, "rides.json")
USERS_FILE = os.path.join(DATA_FOLDER, "users.json")


def load_rides():

    if not os.path.exists(RIDES_FILE):
        return []

    with open(RIDES_FILE) as f:
        return json.load(f)


def save_rides(rides):

    with open(RIDES_FILE, "w") as f:
        json.dump(rides, f, indent=4)


def load_users():

    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE) as f:
        return json.load(f)


def save_users(users):

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)