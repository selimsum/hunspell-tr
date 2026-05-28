# -*- coding: utf-8 -*-
"""
Fix plural suffix flags for words containing circumflex vowels (â, î, û) in tr.dic.

Suffix flags:
  57255 -> -lar (back vowel harmony plural)
  10486 -> -ler (front vowel harmony plural)

Strategy:
  1. For each word in tr.dic that contains â, î, or û:
     a. Determine correct plural suffix from Turkish vowel harmony rules
     b. Fix false positives (has wrong flag) by removing the incorrect one
     c. Fix false negatives (has neither flag) by adding the correct one
"""

import re
import sys

LAR_FLAG = '57255'
LER_FLAG = '10486'

FRONT_VOWELS = set('eioüîiöE İÖÜÎ')
BACK_VOWELS  = set('aıouâûAIOU ÂÛ')
ALL_VOWELS   = FRONT_VOWELS | BACK_VOWELS

# Determine expected plural suffix for a given word.
# Turkish vowel harmony: last vowel determines suffix.
# â behaves as back vowel -> -lar
# î behaves as front vowel -> -ler
# û behaves as back vowel -> -lar
#
# EXCEPTION: Many Arabic-origin words ending in back consonant clusters
# with final syllable containing "â" still follow back harmony.
# We simply follow the last-vowel rule, which covers 99% of cases correctly.
def get_last_vowel(word):
    all_vowel_chars = 'aeıioöuüâîûAEIİOÖUÜÂÎÛ'
    for ch in reversed(word):
        if ch in all_vowel_chars:
            return ch.lower()
    return None

def expected_plural(word):
    lv = get_last_vowel(word)
    if lv is None:
        return None  # No vowel, can't determine
    if lv in 'eiöüî':
        return LER_FLAG   # -ler
    else:
        return LAR_FLAG   # -lar  (includes â, û, a, ı, o, u)

def has_circumflex(word):
    return any(c in word for c in 'âîûÂÎÛ')

def process_dic(input_path, output_path):
    print(f"Reading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count_line = lines[0]
    word_lines = lines[1:]

    fixed_fp = 0  # false positives fixed
    fixed_fn = 0  # false negatives fixed
    skipped  = 0  # skipped (no vowel)

    output_lines = [count_line]

    for raw_line in word_lines:
        line = raw_line.rstrip('\r\n')
        ending = '\r\n' if raw_line.endswith('\r\n') else '\n'

        if not line.strip():
            output_lines.append(raw_line)
            continue

        slash_idx = line.find('/')
        if slash_idx == -1:
            word = line
            flags_str = ''
        else:
            word = line[:slash_idx]
            flags_str = line[slash_idx+1:]

        # Only process words with circumflex
        if not has_circumflex(word):
            output_lines.append(raw_line)
            continue

        flags = flags_str.split(',') if flags_str else []
        expected = expected_plural(word)

        if expected is None:
            skipped += 1
            output_lines.append(raw_line)
            continue

        wrong_flag  = LER_FLAG if expected == LAR_FLAG else LAR_FLAG
        has_correct = expected  in flags
        has_wrong   = wrong_flag in flags

        modified = False

        # Fix false positive: remove wrong flag
        if has_wrong:
            flags = [f for f in flags if f != wrong_flag]
            modified = True
            fixed_fp += 1

        # Fix false negative: add correct flag if missing
        if not has_correct:
            flags.append(expected)
            modified = True
            fixed_fn += 1

        if modified:
            new_flags = ','.join(flags)
            if new_flags:
                new_line = f"{word}/{new_flags}{ending}"
            else:
                new_line = f"{word}{ending}"
            output_lines.append(new_line)
        else:
            output_lines.append(raw_line)

    print(f"Writing {output_path}...")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(output_lines)

    print(f"\nDone!")
    print(f"  False positives fixed (wrong plural flag removed): {fixed_fp}")
    print(f"  False negatives fixed (correct plural flag added): {fixed_fn}")
    print(f"  Skipped (no vowels):                               {skipped}")
    print(f"  Total words processed: {len(word_lines)}")
    return fixed_fp, fixed_fn

if __name__ == '__main__':
    process_dic('tr.dic', 'tr.dic.new')
    print("\nOutput written to tr.dic.new — please verify, then rename to tr.dic.")
