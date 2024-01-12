import tkinter as tk
import psutil
import time
import threading
import json
import math

UPDATE_DELAY = 1
stay_logged_in = False
payload_file = 'network_data.json'

def get_size(bytes):
    if bytes == 0:
        return "0B"
    sizes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    size = round(bytes / p, 2)
    return f"{size}{sizes[i]}"

def save_network_data(sent, received):
    with open(payload_file, 'w') as file:
        json.dump({'sent': sent, 'received': received}, file)

def start_stop_monitoring():
    global stay_logged_in
    if not stay_logged_in:
        stay_logged_in = True
        start_button.config(text="Stop Monitoring")
        start_monitoring_thread()
    else:
        stay_logged_in = False
        start_button.config(text="Start Monitoring")

def monitor_network():
    sent_data = 0
    received_data = 0

    while stay_logged_in:
        io = psutil.net_io_counters()
        bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv

        time.sleep(UPDATE_DELAY)

        io_2 = psutil.net_io_counters()
        sent_speed = io_2.bytes_sent - bytes_sent
        recv_speed = io_2.bytes_recv - bytes_recv

        sent_data += sent_speed
        received_data += recv_speed

        sent_text = get_size(sent_data)
        recv_text = get_size(received_data)

        upload_label.config(text=f"Upload: {sent_text}")
        download_label.config(text=f"Download: {recv_text}")

    save_network_data(sent_data, received_data)

def start_monitoring_thread():
    network_thread = threading.Thread(target=monitor_network)
    network_thread.start()

root = tk.Tk()
root.title("Network Usage Monitor")

upload_label = tk.Label(root, text="Upload: 0B")
upload_label.pack()

download_label = tk.Label(root, text="Download: 0B")
download_label.pack()

start_button = tk.Button(root, text="Start Monitoring", command=start_stop_monitoring)
start_button.pack(pady=20)

# Attempt to load previous data when the application starts
try:
    with open(payload_file, 'r') as file:
        data = json.load(file)
        # Display loaded data in the labels
        upload_label.config(text=f"Upload: {get_size(data['sent'])}")
        download_label.config(text=f"Download: {get_size(data['received'])}")
        print(f"Loaded previous data - Upload: {get_size(data['sent'])}, Download: {get_size(data['received'])}")
except FileNotFoundError:
    print("No previous data found.")

root.mainloop()
