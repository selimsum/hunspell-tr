# -*- coding: utf-8 -*-
"""
Compress Hunspell Turkish Dictionary files using AF flag aliasing.
This is a lossless compression technique that replaces long lists of comma-separated 
numbers in tr.dic with a single index pointing to an AF alias defined in tr.aff.
"""

import os
import sys

def compress(aff_path, dic_path, aff_out_path, dic_out_path):
    print("Step 1: Reading and parsing tr.dic...")
    words_data = []
    flag_sets = []
    
    with open(dic_path, 'r', encoding='utf-8') as f:
        # First line is count
        count_line = f.readline().strip()
        
        for line in f:
            line = line.rstrip('\r\n')
            if not line.strip():
                continue
                
            slash_idx = line.find('/')
            if slash_idx != -1:
                word = line[:slash_idx]
                flags_str = line[slash_idx+1:]
                # Split and sort to ensure duplicates with different orders are normalized
                flags = tuple(sorted(flags_str.split(',')))
                words_data.append((word, flags))
                flag_sets.append(flags)
            else:
                words_data.append((line, None))
                
    print(f"Loaded {len(words_data)} words.")
    
    print("Step 2: Identifying unique flag combinations...")
    # Get unique sets and preserve a stable order
    unique_flag_sets = []
    seen = set()
    for fs in flag_sets:
        if fs not in seen:
            seen.add(fs)
            unique_flag_sets.append(fs)
            
    print(f"Total unique flag combinations: {len(unique_flag_sets)}")
    
    # Create a mapping for quick lookup
    flag_set_to_index = {fs: i + 1 for i, fs in enumerate(unique_flag_sets)}
    
    print("Step 3: Writing compressed tr.dic...")
    with open(dic_out_path, 'w', encoding='utf-8', newline='') as f:
        f.write(f"{len(words_data)}\n")
        for word, flags in words_data:
            if flags:
                idx = flag_set_to_index[flags]
                f.write(f"{word}/{idx}\n")
            else:
                f.write(f"{word}\n")
    print(f"Compressed dictionary written to {dic_out_path}")
    
    print("Step 4: Writing compressed tr.aff with AF definitions...")
    with open(aff_path, 'r', encoding='utf-8') as f_in:
        aff_lines = f_in.readlines()
        
    # Find the line containing "FLAG num"
    flag_num_idx = -1
    for i, line in enumerate(aff_lines):
        if line.strip() == "FLAG num":
            flag_num_idx = i
            break
            
    if flag_num_idx == -1:
        print("Error: Could not find 'FLAG num' in the affix file.")
        sys.exit(1)
        
    print(f"Found 'FLAG num' at line {flag_num_idx + 1}")
    
    # Assemble the new affix file content
    new_aff_content = []
    # 1. Header (up to and including FLAG num)
    for i in range(flag_num_idx + 1):
        new_aff_content.append(aff_lines[i])
        
    # 2. AF Table
    new_aff_content.append(f"\n# AF Flag Aliasing Compression Table\n")
    new_aff_content.append(f"AF {len(unique_flag_sets)}\n")
    for fs in unique_flag_sets:
        # Join with commas since they are FLAG num
        flags_str = ','.join(fs)
        new_aff_content.append(f"AF {flags_str}\n")
    new_aff_content.append("\n")
    
    # 3. Rest of the file (from FLAG num to end)
    for i in range(flag_num_idx + 1, len(aff_lines)):
        new_aff_content.append(aff_lines[i])
        
    with open(aff_out_path, 'w', encoding='utf-8', newline='') as f_out:
        f_out.writelines(new_aff_content)
        
    print(f"Compressed affix file written to {aff_out_path}")
    print("Compression complete!")

if __name__ == '__main__':
    compress('tr.aff', 'tr.dic', 'tr.aff.new', 'tr.dic.new')
