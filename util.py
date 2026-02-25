import hashlib
import logging
import os

logger = logging.getLogger('urnik.util')


def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)

    digest = hash_func.hexdigest()
    logger.debug('Hash of %s: %s', file_path, digest)
    return digest


def remove_file(file_path):
    try:
        os.remove(file_path)
        logger.debug('Removed file: %s', file_path)
    except Exception as e:
        logger.warning('Could not remove %s: %s', file_path, e)


def save_hash(file_hash, file_path):
    try:
        with open(f'{file_path}.txt', 'w', encoding='utf-8') as file:
            file.write(file_hash)
        logger.debug('Saved hash to %s.txt', file_path)
    except FileNotFoundError:
        logger.error('File not found: %s', file_path)
    except Exception as e:
        logger.error('Error saving hash: %s', e)


def read_hash(file_path):
    try:
        with open(f'{file_path}.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ''
    except Exception as e:
        logger.error('Error reading hash file: %s', e)
        return ''
