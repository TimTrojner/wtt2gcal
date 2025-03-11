import hashlib
import os

def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()

def remove_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(e)

def save_hash(file_hash, file_path):
    try:
        with open(f'{file_path}.txt', 'w', encoding='utf-8') as file:
            file.write(file_hash)
    except FileNotFoundError:
        print(f'File {file_path} not found')
    except Exception as e:
        print(e)

def read_hash(file_path):
    try:
        with open(f'{file_path}.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ''
    except Exception as e:
        print(f'Error reading file: {e}')
        return ''
