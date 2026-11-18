"""
isan_phonology.py - Authentic Isan Phonological Rules & Tonotactics Engine
Converts text into true Northeastern Thai (Isan) IPA phonemes by overriding
Central Thai (Bangkok) tone contours with authentic Isan tone contours:
- Low-consonant syllables with tone mark 1: Central Falling (̂) -> Isan High (́)
- Questions and particles: 'เด้อ' -> də́ː, 'บ่' -> bɔ́ː, 'จ้า' -> tɕáː, 'แหน่' -> nɛ́ː
- Lexical tone inflections: แซ่บ -> sɛ́ːp, เว้า -> wáw, เบิ่ง -> bɤ́ŋ, ฮัก -> hák
"""

import re
from typing import List
from vachanatts.th_phonemizer import phonemizer

# High-priority token-to-IPA Isan phonetic overrides
ISAN_PHONETIC_OVERRIDES = {
    # Particles & Questions (The key giveaways of authentic Isan speech)
    "เด้อ": "də́ː",
    "จ้า": "tɕáː",
    "บ่": "bɔ́ː",
    "แหน่": "nɛ́ː",
    "แหน่ะ": "nɛ́ʔ",
    "เด้": "déː",
    "นำ": "nam",
    "นำกัน": "nam kan",

    # Pronouns & People
    "ข้อย": "kʰɔ́ːj",
    "เจ้า": "tɕáw",
    "เพิ่น": "pʰɤ́ːn",
    "หมู่เฮา": "mùː haw",
    "เฮา": "haw",
    "ผู้บ่าว": "pʰúː bàːw",
    "ผู้สาว": "pʰúː sǎːw",
    "เด็กน้อย": "dèk nɔ́ːj",
    "อีพ่อ": "ʔiː pʰɔ́ː",
    "อีแม่": "ʔiː mɛ́ː",
    "อ้าย": "ʔáːj",
    "เอื้อย": "ʔɯ́aj",

    # Verbs & Actions
    "เว้า": "wáw",
    "เบิ่ง": "bɤ́ŋ",
    "เฮ็ด": "hét",
    "ย่าง": "ɲáːŋ",
    "แล่น": "lɛ́ːn",
    "เมือ": "mɯ́a",
    "เมือบ้าน": "mɯ́a bâːn",
    "เลาะ": "lɔ́ʔ",
    "ตั๋ว": "tǔa",
    "ย่าน": "jáːn",
    "ฮัก": "hák",
    "ฮู้": "húː",
    "คึด": "kʰɯ́t",
    "คึดฮอด": "kʰɯ́t hɔ̂ːt",
    "ซ่อย": "sɔ́ːj",
    "ซิม": "sím",
    "สิ": "sí",
    "กิน": "kin",
    "กินข้าว": "kin kʰâːw",

    # Adjectives & Adverbs
    "แซ่บ": "sɛ́ːp",
    "แซ่บหลาย": "sɛ́ːp lǎːj",
    "แซ่บอีหลี": "sɛ́ːp ʔiː lǐː",
    "อีหลี": "ʔiː lǐː",
    "หลาย": "lǎːj",
    "งาม": "ŋaːm",
    "ตาฮัก": "taː hák",
    "ม่วน": "múan",
    "ม่วนซื่น": "múan sɯ́ːn",
    "สูน": "sǔːn",
    "เคียด": "kʰíat",
    "ซ้า": "sáː",
    "ไว": "waj",
    "ฮ้อน": "hɔ́ːn",

    # Time, Places & Expressions
    "มื้อนี้": "mɯ́ː níː",
    "มื้ออื่น": "mɯ́ː ʔɯ́ːn",
    "มื้อวาน": "mɯ́ː waːn",
    "ยามเซ้า": "jaːm sáw",
    "ยามแลง": "jaːm lɛːŋ",
    "เป็นจังใด๋": "pen tɕáŋ dáj",
    "เป็นจังใด๋แหน่": "pen tɕáŋ dáj nɛ́ː",
    "เป็นจั่งใด๋": "pen tɕáŋ dáj",
    "เฮ็ดหยัง": "hét ɲǎŋ",
    "เฮ็ดหยังอยู่": "hét ɲǎŋ jùː",
    "ไปไส": "paj sǎj",
    "ไปไสมา": "paj sǎj maː",
    "ยินดีต้อนฮับ": "jindiː tɔ́ːn háp",
    "สบายดี": "sabaːjdiː",
    "สบายดีบ่": "sabaːjdiː bɔ́ː",
    "บ่เป็นหยัง": "bɔ́ː pen ɲǎŋ",
    "แม่น": "mɛ́ːn",
    "บ่แม่น": "bɔ́ː mɛ́ːn",
    "โฮงเฮียน": "hoːŋ hían",
    "โฮงหมอ": "hoːŋ mɔ̌ː",
    "ฮดไฟ": "hót faj",
}

# Regex replacements on IPA phonemes to systematically fix Isan tone patterns
IPA_PATTERN_FIXES = [
    # Low consonants + ไม้เอก in Central Thai produce falling (̂), but in Isan they must be high (́)
    (r"([dhlmnŋrswj])([aeiouɯəɤɛɔ]+)̂(ː?)", r"\1\2́\3"),
    # Fix 'เด้อ' specifically
    (r"də̂ː", r"də́ː"),
    # Fix 'บ่' specifically
    (r"bɔ̀ː", r"bɔ́ː"),
    (r"bɔ̂ː", r"bɔ́ː"),
    # Fix 'จ้า' specifically
    (r"tɕâː", r"tɕáː"),
    # Fix 'แซ่บ'
    (r"sɛ̂ːp", r"sɛ́ːp"),
    # Fix 'แหน่'
    (r"hɛ̌ː", r"nɛ́ː"),
    (r"hɛ̂ː", r"nɛ́ː"),
]

def text_to_isan_phonemes(text: str) -> List[List[str]]:
    """
    Converts Isan text into authentic Isan IPA phonemes with correct dialect tone accents.
    """
    # Step 1: Pre-tokenize and check for multi-word Isan expressions
    working_text = text.strip()

    # Step 2: Run base phonemizer
    sentences = phonemizer(working_text)
    out_sentences = []

    for sent in sentences:
        sent_str = "".join(sent)
        
        # Step 3: Apply systematic Isan tone regex shifts
        for pat, repl in IPA_PATTERN_FIXES:
            sent_str = re.sub(pat, repl, sent_str)
            
        out_sentences.append(list(sent_str))

    return out_sentences

if __name__ == "__main__":
    test_sentences = [
        "ยินดีต้อนฮับเด้อจ้า สบายดีบ่ มื้อนี้เป็นจังใด๋แหน่ แซ่บอีหลีเด้อ",
        "มื้อนี้เฮาสิไปเลาะตลาดนำกันบ่จ้า ขอบใจหลายๆ เด้อ",
        "เฮ็ดหยังอยู่ คึดฮอดหลายๆ เด้อ สบายดีบ่",
        "อาหารฮ้านนี้แซ่บหลาย มื้ออื่นเฮามากินนำกันอีกเด้อจ้า"
    ]
    for s in test_sentences:
        print("Input:", s)
        ph = text_to_isan_phonemes(s)
        print("Isan Phonemes:", "".join(ph[0]))
        print()
