import argparse
import string
import os

# Encrypts the given text using a substitution cipher based on the key.
# The key must be 26 unique lowercase letters.
def encrypt(text, key):
    if not(key.isalpha() and key.islower() and len(set(key)) == 26):
        raise ValueError("Key must be 26 unique lowercase letters only.")
    text = ''.join(filter(str.isalpha, text))  # Remove non-alphabetic characters
    table = str.maketrans(string.ascii_lowercase, key)
    return text.translate(table)

# Decrypts a message that was encrypted with the substitution cipher.
# The same key used for encryption must be provided.
def decrypt(text, key):
    if not (key.isalpha() and key.islower() and len(set(key)) == 26):
        raise ValueError("Key must be 26 unique lowercase letters only.")
    table = str.maketrans(key, string.ascii_lowercase)
    return text.translate(table)

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().lower()

def write_file(file_path, crypMes):
    with open(file_path, 'w') as file:
        file.write(crypMes)

def args_process():
    parser = argparse.ArgumentParser(description='Encrypt or decrypt messages with a provided key.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--encrypt', metavar='KEY', help='Encrypt the message with the provided key. NOTE: the key must be 26 lowercase unique letters.')
    group.add_argument('--decrypt', metavar='KEY', help='Decrypt the message with the provided key. NOTE: the key must be 26 lowercase unique letters.')
    parser.add_argument('--out', metavar='OUTFILE', help='File to write the result')
    parser.add_argument('file', metavar='FILE', help='Input file containing the message')
    return parser.parse_args()

def main():
    args = args_process()
    text = read_file(args.file)

    if args.encrypt:
        result = encrypt(text, args.encrypt)
    elif args.decrypt:
        result = decrypt(text, args.decrypt)

    if args.out:
        write_file(args.out, result)
    else:
        print(result)

if __name__ == '__main__':
    main()
