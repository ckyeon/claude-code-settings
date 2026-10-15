import time


def send(user, message, retries=3):
    for attempt in range(retries):
        try:
            print(f"to {user}: {message}")
            return True
        except OSError:
            time.sleep(2 ** attempt)
    return False
