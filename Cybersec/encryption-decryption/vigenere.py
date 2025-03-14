import argparse
import string
import os

# Encrypts the given text using a Vigenère cipher.
# Each character is shifted by the position of the corresponding character in the key.
def encrypt(text, key):
    text = ''.join(filter(str.isalpha, text.lower()))  # Keep only letters and convert to lowercase
    key = key.lower()
    encrypted_text = []

    for i, char in enumerate(text):
        shift = ord(key[i % len(key)]) - ord('a')  # Calculate shift based on key character
        encrypted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
        encrypted_text.append(encrypted_char)

    return ''.join(encrypted_text)

# Decrypts a message encoded with the Vigenère cipher using the same key.
def decrypt(text, key):
    text = ''.join(filter(str.isalpha, text.lower()))
    key = key.lower()
    decrypted_text = []

    for i, char in enumerate(text):
        shift = ord(key[i % len(key)]) - ord('a')  # Reverse the shift applied during encryption
        decrypted_char = chr((ord(char) - ord('a') - shift + 26) % 26 + ord('a'))
        decrypted_text.append(decrypted_char)

    return ''.join(decrypted_text)

# Reads and returns the contents of a file as lowercase text.
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().lower()

# Writes the encrypted/decrypted message to the specified output file.
def write_file(file_path, crypMes):
    with open(file_path, 'w') as file:
        file.write(crypMes)

# Parses and validates command-line arguments for encryption/decryption.
def args_process():
    parser = argparse.ArgumentParser(description='Encrypt or decrypt messages with a provided key.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--encrypt', metavar='KEY',
                       help='Encrypt the message with the provided key. NOTE: key can be any string of letters.')
    group.add_argument('--decrypt', metavar='KEY',
                       help='Decrypt the message with the provided key. NOTE: key must match the one used for encryption.')
    parser.add_argument('--out', metavar='OUTFILE', help='File to write the result')
    parser.add_argument('file', metavar='FILE', help='Input file containing the message')
    return parser.parse_args()

# Main routine: reads input file, performs encryption/decryption, writes or prints the result.
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
