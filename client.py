import socket
import os
import sys
import time
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Funkcja do wyłączenia systemu operacyjnego
def shutdown():
    try:
        if os.name == 'nt': # Windows
            subprocess.call(['shutdown', '/s', '/t', '0'])
        elif os.name == 'posix': # Unix
            if sys.platform == "darwin": # macOS
                subprocess.call(['shutdown', '-h', 'now'])
            else: # Linux i inne
                subprocess.call(['shutdown', 'now'])
    except Exception as e:
        print(f"Failed to shutdown: {e}")

# Klasa klienta do zarządzania połączeniem i komunikacją z serwerem
class Client:
    def __init__(self, update_message_func):
        self.client_socket = None
        self.running = False
        self.details_thread_running = False
        self.update_message_func = update_message_func

    # Funkcja do nawiązania połączenia z serwerem
    def connect(self, address, port):
        self.address = address
        self.port = port
        self.start_client()

    # Funkcja do rozpoczęcia wątku klienta
    def start_client(self):
        self.running = True
        threading.Thread(target=self.run_client, daemon=True).start()

    # Funkcja do aktualizacji statusu klienta
    def update_status(self, status):
        self.update_message_func(status)

    # Funkcja do uruchomienia wątku klienta, obsługująca odbieranie i wysyłanie wiadomości
    def run_client(self):
        while self.running:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.address, self.port))
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

    # Funkcja do zatrzymania klienta i zamknięcia połączenie z serwerem
    def stop_client(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()

    # Funkcja do obsługi komend od serwera
    def handle_server_message(self, message):
        message = message.strip()
        if message == "shutdown":
            self.stop_client()
            time.sleep(1)
            shutdown()
        elif message == "disconnect":
            self.stop_client() 
            self.update_status("Status: Disconnected")

# Klasa GUI klienta umożliwiająca interakcję z użytkownikiem
class ClientGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Remote shutdown system")
        self.root.geometry("600x400")

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

    # Funkcja do aktualizacji statusu klienta w GUI
    def update_status(self, status):
        self.status_label.config(text=status)

    # Funkcja do łączenia klienta z serwerem
    def connect_to_server(self):
        address = self.server_address_entry.get()
        port = int(self.server_port_entry.get())
        try:
            self.client.connect(address, port)
            self.status_label.config(text="Status: Connected")
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))
            self.status_label.config(text="Status: Connection failed")

    # Funkcja do rozłączania klienta z serwerem
    def disconnect_from_server(self):
        self.client.stop_client()
        self.status_label.config(text="Status: Disconnected")

    # Funkcja do aktualizacji wiadomości w GUI
    def update_message(self, message):
        self.messages.insert(tk.END, message + '\n')

    # Funkcja do uruchomienia GUI klienta
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Funkcja do aktualizacji statusu klienta w GUI
    def update_message_func(message):
        if message.startswith("Status:"):
            client_gui.update_status(message)
        else:
            client_gui.update_message(message)

    client = Client(update_message_func)
    client_gui = ClientGUI(client)
    client_gui.run()
