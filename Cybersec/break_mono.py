from collections import Counter
import collections
import string
import argparse

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().lower()

def derive_key(file_path):
    english_frequency_order = "etnsaiohrdclugfybmpwvkjqxz"  #frequency derived from internet and common.txt
    
    text = read_file(file_path)
    
    letter_counts = Counter(c for c in text if c.isalpha())
    
    sorted_letters_by_freq = [item[0] for item in letter_counts.most_common()]
    
    all_letters = set('abcdefghijklmnopqrstuvwxyz')
    used_letters = set(sorted_letters_by_freq)
    missing_letters = list(all_letters - used_letters)      #in case a letter was not used in the text, it will be pushed to the end
    
    missing_letters.sort()
    
    frequency_map = {english_frequency_order[i]: sorted_letters_by_freq[i] for i in range(len(sorted_letters_by_freq))}
    
    mapped_alphabet = ''.join(frequency_map.get(letter, '') for letter in 'abcdefghijklmnopqrstuvwxyz')     
    mapped_alphabet += ''.join(missing_letters)             #joining the key with thge unused letters to get the final monoalphabetic key
    
    return mapped_alphabet


#argument processor module
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