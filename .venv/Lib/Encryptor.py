import struct

class Encryptor:
    def __init__(self, rc5_algorithm, block_size=8, buffer_size=1024 * 64):
        self.rc5 = rc5_algorithm
        self.block_size = block_size
        self.buffer_size = buffer_size

    def encrypt_file(self, file_path):
        encrypted_data = bytearray()
        original_length = 0

        with open(file_path, 'rb') as file:
            # Читаємо файл блоками
            while True:
                block = file.read(self.buffer_size)
                if not block:
                    break


                original_length += len(block)


                for i in range(0, len(block), self.block_size):
                    block_data = block[i:i + self.block_size]
                    if len(block_data) < self.block_size:

                        block_data += b'\x00' * (self.block_size - len(block_data))
                    encrypted_block = self.rc5.encrypt_block(block_data)
                    encrypted_data.extend(encrypted_block)


        length_bytes = struct.pack('<Q', original_length)


        encrypted_data = length_bytes + encrypted_data

        return encrypted_data

    def save_encrypted_file(self, file_path, encrypted_data):
        encrypted_file_path = file_path + '.enc'
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)
        return encrypted_file_path
