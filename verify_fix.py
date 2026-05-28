# -*- coding: utf-8 -*-
"""
Verify the fixed tr.dic.new against expected plural behavior.
"""

LAR_FLAG = '57255'
LER_FLAG = '10486'

def get_last_vowel(word):
    all_vowel_chars = 'aeıioöuüâîûAEIİOÖUÜÂÎÛ'
    for ch in reversed(word):
        if ch in all_vowel_chars:
            return ch.lower()
    return None

def expected_plural(word):
    lv = get_last_vowel(word)
    if lv is None:
        return None
    if lv in 'eiöüî':
        return LER_FLAG
    else:
        return LAR_FLAG

def has_circumflex(word):
    return any(c in word for c in 'âîûÂÎÛ')

def verify(path):
    print(f"Verifying {path}...")
    remaining_fp = []
    remaining_fn = []
    correct = 0

    with open(path, 'r', encoding='utf-8') as f:
        f.readline()  # count line
        for line in f:
            line = line.strip()
            if not line:
                continue
            slash_idx = line.find('/')
            if slash_idx == -1:
                word, flags = line, []
            else:
                word = line[:slash_idx]
                flags = line[slash_idx+1:].split(',')

            if not has_circumflex(word):
                continue

            expected = expected_plural(word)
            if expected is None:
                continue

            wrong_flag  = LER_FLAG if expected == LAR_FLAG else LAR_FLAG
            has_correct = expected   in flags
            has_wrong   = wrong_flag in flags

            if has_wrong:
                remaining_fp.append((word, f"Still has wrong flag {wrong_flag}"))
            elif not has_correct:
                remaining_fn.append((word, f"Still missing correct flag {expected}"))
            else:
                correct += 1

    print(f"  Correct:           {correct}")
    print(f"  Still FP (wrong flag): {len(remaining_fp)}")
    for w, r in remaining_fp[:20]:
        print(f"    * {w} -> {r}")
    print(f"  Still FN (missing flag): {len(remaining_fn)}")
    for w, r in remaining_fn[:20]:
        print(f"    * {w} -> {r}")
    print()
    return len(remaining_fp), len(remaining_fn)

if __name__ == '__main__':
    fp, fn = verify('tr.dic.new')
    if fp == 0 and fn == 0:
        print("All checks passed. Safe to replace tr.dic.")
    else:
        print(f"Issues remain: {fp} FP, {fn} FN. Do NOT replace tr.dic yet.")
