# -*- coding: utf-8 -*-
"""
Verify Hunspell dictionary compression.
Runs hunspell on a dataset of words using both the original and compressed dictionary
configurations, then compares their output to guarantee identical behavior.
"""

import csv
import subprocess
import sys
import os

def load_test_words(csv_path, max_words=1000):
    print(f"Loading test words from {csv_path}...")
    words = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # skip header "gold,input"
        for row in reader:
            if len(row) >= 2:
                gold, input_word = row[0].strip(), row[1].strip()
                if gold:
                    words.append(gold)
                if input_word:
                    words.append(input_word)
            if len(words) >= max_words:
                break
    return sorted(list(set(words))) # Deduplicate and sort

def run_hunspell(dict_base_path, words):
    # Runs hunspell -d <dict_base_path> -a
    # Passing words through stdin. Returns list of output lines.
    # Note: Hunspell output starts with a header line like:
    # @(#) International Ispell Version 3.2.06 (but really Hunspell 1.7.0)
    process = subprocess.Popen(
        ['hunspell', '-d', dict_base_path, '-a'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    # Write words separated by newlines
    input_data = '\n'.join(words) + '\n'
    stdout, stderr = process.communicate(input=input_data)
    
    if process.returncode != 0:
        print(f"Error running hunspell for {dict_base_path}: {stderr}")
        sys.exit(1)
        
    lines = stdout.splitlines()
    # Strip the header line if present
    if lines and lines[0].startswith('@(#)'):
        lines = lines[1:]
        
    # Filter empty lines
    lines = [line.strip() for line in lines if line.strip()]
    return lines

def main():
    csv_path = 'trspell10.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        sys.exit(1)
        
    words = load_test_words(csv_path, max_words=1000)
    print(f"Loaded {len(words)} unique test words.")
    
    # Check if files exist
    if not os.path.exists('tr.aff') or not os.path.exists('tr.dic'):
        print("Error: Original dictionary files tr.aff and tr.dic must exist.")
        sys.exit(1)
        
    if not os.path.exists('tr.aff.new') or not os.path.exists('tr.dic.new'):
        print("Error: Compressed dictionary files tr.aff.new and tr.dic.new not found. Please run compress_dictionary.py first.")
        sys.exit(1)
        
    # For hunspell -d to work on tr.new, we need tr.new.aff and tr.new.dic.
    # We will copy them temporarily or just rename/symlink if needed.
    # Actually, let's copy them to temporary names in the current directory:
    # tr_new.aff and tr_new.dic.
    import shutil
    shutil.copyfile('tr.aff.new', 'tr_new.aff')
    shutil.copyfile('tr.dic.new', 'tr_new.dic')
    
    try:
        print("Running hunspell on original dictionary (tr)...")
        original_output = run_hunspell('tr', words)
        
        print("Running hunspell on compressed dictionary (tr_new)...")
        compressed_output = run_hunspell('tr_new', words)
        
        print("Comparing outputs...")
        if len(original_output) != len(compressed_output):
            print(f"Mismatch: Original output has {len(original_output)} lines, compressed has {len(compressed_output)} lines.")
            # Print a snippet of differences
            for i in range(min(len(original_output), len(compressed_output))):
                if original_output[i] != compressed_output[i]:
                    print(f"Line {i} mismatch:")
                    print(f"  Orig: {original_output[i]}")
                    print(f"  New:  {compressed_output[i]}")
                    break
            sys.exit(1)
            
        mismatch_count = 0
        for i in range(len(original_output)):
            if original_output[i] != compressed_output[i]:
                if mismatch_count < 10:
                    print(f"Mismatch at word index {i}:")
                    print(f"  Orig: {original_output[i]}")
                    print(f"  New:  {compressed_output[i]}")
                mismatch_count += 1
                
        if mismatch_count > 0:
            print(f"Verification failed with {mismatch_count} mismatches.")
            sys.exit(1)
            
        print("Verification successful! Zero behavioral divergence detected between original and compressed files.")
        
    finally:
        # Clean up temporary files
        if os.path.exists('tr_new.aff'):
            os.remove('tr_new.aff')
        if os.path.exists('tr_new.dic'):
            os.remove('tr_new.dic')

if __name__ == '__main__':
    main()
