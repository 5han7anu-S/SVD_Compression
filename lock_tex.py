import os
import sys
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

# Derive a symmetric key from a password
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

def encrypt_file(file_path: str, password: str):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(12)  # 96-bit IV for AES-GCM

    with open(file_path, 'rb') as f:
        data = f.read()
    
    aesgcm = AESGCM(key)
    encrypted_data = aesgcm.encrypt(iv, data, None)
    
    with open(file_path + ".enc", 'wb') as f:
        f.write(salt + iv + encrypted_data)

def decrypt_file(file_path: str, password: str):
    with open(file_path, 'rb') as f:
        salt = f.read(16)
        iv = f.read(12)
        encrypted_data = f.read()
    
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    try:
        decrypted_data = aesgcm.decrypt(iv, encrypted_data, None)
        original_file_path = file_path[:-4]  # Remove .enc extension
        with open(original_file_path, 'wb') as f:
            f.write(decrypted_data)
        return True
    except InvalidTag:
        return False

def encrypt_folder(folder_path: str, password: str):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            encrypt_file(file_path, password)
            os.remove(file_path) 

def decrypt_folder(folder_path: str, password: str):
    success = True
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".enc"):
                file_path = os.path.join(root, file)
                if decrypt_file(file_path, password):
                    os.remove(file_path)
                else:
                    success = False

    return success

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder_path> <(e|encrypt) | (d|decrypt)>")
        sys.exit(1)

    folder_path = sys.argv[1]
    action = sys.argv[2].strip().lower()
    
    if action in ['e', 'encrypt']:
        password = getpass.getpass("Enter password: ")
        encrypt_folder(folder_path, password)
        print(f"{folder_path} has been encrypted.")
    elif action in ['d', 'decrypt']:
        while True:
            password = getpass.getpass("Enter password: ")
            if decrypt_folder(folder_path, password):
                print(f"{folder_path} has been decrypted.")
                break
            else:
                print("Incorrect password.")
    else:
        print("Invalid Input")
        print("Usage: python script.py <folder_path> <(e|encrypt) | (d|decrypt)>")
        sys.exit(1)
