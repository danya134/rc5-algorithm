import struct
import os

class Decryptor:
    def __init__(self, rc5_algorithm, block_size=8, buffer_size=1024 * 64):
        self.rc5 = rc5_algorithm
        self.block_size = block_size
        self.buffer_size = buffer_size

    def decrypt_file(self, file_path):
        decrypted_data = bytearray()
        original_length = None

        with open(file_path, 'rb') as file:
            # Читаємо перші 8 байт для отримання оригінальної довжини
            length_bytes = file.read(8)
            if len(length_bytes) < 8:
                raise ValueError("Invalid encrypted file: Missing length data.")
            original_length = struct.unpack('<Q', length_bytes)[0]

            # Читаємо зашифровані дані блоками
            while True:
                block = file.read(self.buffer_size)
                if not block:
                    break


                for i in range(0, len(block), self.block_size):
                    block_data = block[i:i + self.block_size]
                    if len(block_data) < self.block_size:
                        break
                    decrypted_block = self.rc5.decrypt_block(block_data)
                    decrypted_data.extend(decrypted_block)


        return decrypted_data[:original_length]

    def save_decrypted_file(self, file_path, decrypted_data):
        decrypted_file_path = file_path.replace('.enc', '.dec')
        with open(decrypted_file_path, 'wb') as file:
            file.write(decrypted_data)
        return decrypted_file_path
