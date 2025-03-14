from collections import Counter
import collections
import string
import argparse

# Reads and returns the lowercase contents of the given file.
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().lower()

# Analyzes character frequency in the file and builds a monoalphabetic substitution key.
# Maps the most frequent letters in the encrypted file to typical English letter frequencies.
def derive_key(file_path):
    english_frequency_order = "etnsaiohrdclugfybmpwvkjqxz"  # Based on common English usage

    text = read_file(file_path)

    # Count how often each letter appears in the text
    letter_counts = Counter(c for c in text if c.isalpha())

    # Sort letters by how often they appear
    sorted_letters_by_freq = [item[0] for item in letter_counts.most_common()]

    # Handle any letters that don't appear in the text
    all_letters = set('abcdefghijklmnopqrstuvwxyz')
    used_letters = set(sorted_letters_by_freq)
    missing_letters = list(all_letters - used_letters)
    missing_letters.sort()

    # Map English frequency order to observed frequencies
    frequency_map = {english_frequency_order[i]: sorted_letters_by_freq[i] for i in range(len(sorted_letters_by_freq))}

    # Construct the key, filling in any missing letters at the end
    mapped_alphabet = ''.join(frequency_map.get(letter, '') for letter in 'abcdefghijklmnopqrstuvwxyz')
    mapped_alphabet += ''.join(missing_letters)

    return mapped_alphabet

def args_process():
    parser = argparse.ArgumentParser(description='Derive the key from provided encrypted file.')
    parser.add_argument('file', metavar='FILE', help='Input file containing the message')
    return parser.parse_args()

def main():
    args = args_process()
    text = read_file(args.file)

    key = derive_key(args.file)
    print(key)

if __name__ == '__main__':
    main()
