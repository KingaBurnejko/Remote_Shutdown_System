import socket
import os
import sys
import time
import threading
import subprocess
# import psutil
# import json
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Zdefiniowanie klasy Details
# class Details:
#     def __init__(self):
#         self.name = socket.gethostname()
#         self.osName = os.name
#         self.cpu = psutil.cpu_percent(4)
#         self.ramUsed = "{:.1f}".format(psutil.virtual_memory()[3] / 1000000000)
#         self.ramTotal = "{:.1f}".format(psutil.virtual_memory()[0] / 1000000000)
#         self.ramPercentage = round(float(self.ramUsed) / float(self.ramTotal) * 100, 2)
#         disk = psutil.disk_usage('/')
#         self.diskTotal = "{:.1f}".format(disk.total / 1000000000)
#         self.diskUsed = "{:.1f}".format(disk.used / 1000000000)
#         self.diskFree = "{:.1f}".format(disk.free / 1000000000)
#         self.diskPercentage = disk.percent

#     def getJson(self):
#         return json.dumps(self.__dict__)

# Funkcje z utils.py
def shutdown():
    try:
        if os.name == 'nt':
            subprocess.call(['shutdown', '/s', '/t', '0'])
        elif os.name == 'posix':
            if sys.platform == "darwin":
                subprocess.call(['shutdown', '-h', 'now'])
            else:
                subprocess.call(['shutdown', 'now'])
    except Exception as e:
        print(f"Failed to shutdown: {e}")

# Zaktualizowana klasa Client
class Client:
    def __init__(self, update_message_func):
        self.client_socket = None
        self.running = False
        self.details_thread_running = False
        self.update_message_func = update_message_func

    def connect(self, address, port):
        self.address = address
        self.port = port
        self.start_client()

    def start_client(self):
        self.running = True
        threading.Thread(target=self.run_client, daemon=True).start()

    def update_status(self, status):
        self.update_message_func(status)

    def run_client(self):
        while self.running:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.address, self.port))
                # Zakomentowane wysyłanie informacji o komputerze
                # self.start_details_thread()
                while self.running:
                    msg = self.client_socket.recv(1024)
                    if not msg:
                        break
                    self.update_message_func(msg.decode('utf-8'))
                    self.handle_server_message(msg.decode('utf-8'))
            except Exception as e:
                print("Failed to connect to server. Retrying...")
                time.sleep(2)
            finally:
                if self.client_socket:
                    self.client_socket.close()
                self.running = False

    def stop_client(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()

    # def start_details_thread(self):
    #     def send_details():
    #         while self.details_thread_running:
    #             try:
    #                 details = Details().getJson()
    #                 self.client_socket.send(bytes(details, 'UTF-8'))
    #                 time.sleep(2)
    #             except Exception as e:
    #                 self.stop()
    #                 break

    #     self.details_thread_running = True
    #     details_thread = threading.Thread(target=send_details, daemon=True)
    #     details_thread.start()

    def stop(self):
        self.running = False
        self.details_thread_running = False
        self.client_socket.close()

    def handle_server_message(self, message):
        message = message.strip()
        if message == "shutdown":
            shutdown()
        elif message == "disconnect":
            self.stop_client() 
            self.update_status("Status: Disconnected")


# Klasa GUI dla klienta
class ClientGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Remote shutdown system")
        self.root.geometry("600x400")  # Ustawienie większych wymiarów okna

        tk.Label(self.root, text="IP address:").pack()
        self.server_address_entry = tk.Entry(self.root)
        self.server_address_entry.pack()
        self.server_address_entry.insert(0, "localhost")

        tk.Label(self.root, text="Port:").pack()
        self.server_port_entry = tk.Entry(self.root)
        self.server_port_entry.pack()
        self.server_port_entry.insert(0, "8080")

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack()

        self.disconnect_button = tk.Button(self.root, text="Disconnect", command=self.disconnect_from_server)
        self.disconnect_button.pack()

        self.status_label = tk.Label(self.root, text="Status: Not connected")
        self.status_label.pack()

        self.messages = scrolledtext.ScrolledText(self.root, height=10)
        self.messages.pack()

    def update_status(self, status):
        self.status_label.config(text=status)

    def connect_to_server(self):
        address = self.server_address_entry.get()
        port = int(self.server_port_entry.get())
        try:
            self.client.connect(address, port)
            self.status_label.config(text="Status: Connected")
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))
            self.status_label.config(text="Status: Connection failed")

    def disconnect_from_server(self):
        self.client.stop_client()
        self.status_label.config(text="Status: Disconnected")

    def update_message(self, message):
        self.messages.insert(tk.END, message + '\n')

    def run(self):
        self.root.mainloop()

# Główny punkt wejścia
if __name__ == "__main__":
    def update_message_func(message):
        if message.startswith("Status:"):
            client_gui.update_status(message)
        else:
            client_gui.update_message(message)

    client = Client(update_message_func)
    client_gui = ClientGUI(client)
    client_gui.run()