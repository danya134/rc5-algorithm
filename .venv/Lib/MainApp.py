import os
import binascii
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import struct

from RC5Algorithm import RC5Algorithm
from Encryptor import Encryptor
from Decryptor import Decryptor

class MainApp:
    def __init__(self, master):
        self.master = master
        master.title("RC5 File Encryption")
        master.geometry("500x400")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#2b2b2b", foreground="#ffffff", font=("Helvetica", 12))
        style.configure("TButton", background="#444444", foreground="#ffffff", font=("Helvetica", 12))
        style.configure("TEntry", fieldbackground="#333333", foreground="#ffffff")
        style.configure("Green.Horizontal.TProgressbar", troughcolor="#333333", background="green")
        style.configure("Red.Horizontal.TProgressbar", troughcolor="#333333", background="red")

        master.configure(bg="#2b2b2b")

        self.label = ttk.Label(master, text="RC5 File Encryption and Decryption")
        self.label.pack(pady=10)

        self.key_label = ttk.Label(master, text="Enter Key (2040 bits):")
        self.key_label.pack()
        self.key_entry = ttk.Entry(master)
        self.key_entry.pack()

        self.generate_key_button = ttk.Button(master, text="Generate Key", command=self.generate_key)
        self.generate_key_button.pack(pady=5)

        self.clear_key_button = ttk.Button(master, text="Clear Key", command=self.clear_key)
        self.clear_key_button.pack(pady=5)

        self.file_label = ttk.Label(master, text="Select File:")
        self.file_label.pack()
        self.file_entry = ttk.Entry(master)
        self.file_entry.pack()
        self.file_button = ttk.Button(master, text="Browse", command=self.browse_file)
        self.file_button.pack(pady=5)

        self.encrypt_button = ttk.Button(master, text="Encrypt File", command=self.start_encryption)
        self.encrypt_button.pack(pady=5)

        self.decrypt_button = ttk.Button(master, text="Decrypt File", command=self.start_decryption)
        self.decrypt_button.pack(pady=5)

        # Прогрес-індикатор
        self.progress = ttk.Progressbar(master, orient='horizontal', mode='determinate', style="Green.Horizontal.TProgressbar")
        self.progress.pack(pady=10, fill=tk.X)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if os.path.getsize(filename) > 209715200:
            messagebox.showwarning("Warning", "The selected file exceeds the 200 MB size limit.")
            return
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filename)

    def generate_key(self):
        key = os.urandom(255)
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, binascii.hexlify(key).decode())

    def clear_key(self):
        self.key_entry.delete(0, tk.END)

    def start_encryption(self):
        file_path = self.file_entry.get()
        if os.path.getsize(file_path) > 209715200:
            messagebox.showwarning("Warning", "The selected file exceeds the 200 MB size limit.")
            return
        threading.Thread(target=self.encrypt_file).start()

    def encrypt_file(self):
        self.progress.configure(style="Green.Horizontal.TProgressbar")
        key_hex = self.key_entry.get()
        key = binascii.unhexlify(key_hex)
        file_path = self.file_entry.get()
        if not key or not file_path:
            messagebox.showwarning("Warning", "Please enter a key and select a file.")
            return

        rc5 = RC5Algorithm(key_length=2040, key=key)
        encryptor = Encryptor(rc5)

        try:
            original_size = os.path.getsize(file_path)
            encrypted_data = bytearray()
            bytes_read = 0
            buffer_size = 4096

            with open(file_path, 'rb') as file:
                while True:
                    block = file.read(buffer_size)
                    if not block:
                        break

                    for i in range(0, len(block), 8):
                        data_block = block[i:i + 8]
                        if len(data_block) < 8:
                            data_block += b'\x00' * (8 - len(data_block))

                        encrypted_data.extend(encryptor.rc5.encrypt_block(data_block))

                    bytes_read += len(block)
                    self.progress['value'] = (bytes_read / original_size) * 100
                    self.master.update_idletasks()


            original_length = len(encrypted_data)
            length_bytes = struct.pack('<Q', original_length)
            encrypted_data = length_bytes + encrypted_data

            encrypted_file_path = encryptor.save_encrypted_file(file_path, encrypted_data)
            messagebox.showinfo("Success", f"File encrypted successfully as {encrypted_file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error encrypting file: {str(e)}")

    def start_decryption(self):
        file_path = self.file_entry.get()
        if os.path.getsize(file_path) > 209715200:  # 200 MB обмеження
            messagebox.showwarning("Warning", "The selected file exceeds the 200 MB size limit.")
            return
        threading.Thread(target=self.decrypt_file).start()

    def decrypt_file(self):
        self.progress.configure(style="Green.Horizontal.TProgressbar")
        key_hex = self.key_entry.get()
        key = binascii.unhexlify(key_hex)
        file_path = self.file_entry.get()
        if not key or not file_path:
            messagebox.showwarning("Warning", "Please enter a key and select a file.")
            return

        rc5 = RC5Algorithm(key_length=2040, key=key)
        decryptor = Decryptor(rc5)

        try:
            original_size = os.path.getsize(file_path)
            decrypted_data = bytearray()
            bytes_read = 0
            buffer_size = 4096

            with open(file_path, 'rb') as file:
                length_bytes = file.read(8)
                original_length = struct.unpack('<Q', length_bytes)[0]

                while True:
                    block = file.read(buffer_size)
                    if not block:
                        break

                    for i in range(0, len(block), 8):
                        block_data = block[i:i + 8]
                        if len(block_data) < 8:
                            break

                        decrypted_block = rc5.decrypt_block(block_data)
                        decrypted_data.extend(decrypted_block)

                    bytes_read += len(block)
                    self.progress['value'] = (bytes_read / original_size) * 100  # Оновлення прогресу
                    self.master.update_idletasks()

            decrypted_file_path = decryptor.save_decrypted_file(file_path, decrypted_data[:original_length])
            messagebox.showinfo("Success", f"File decrypted successfully as {decrypted_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error decrypting file: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
