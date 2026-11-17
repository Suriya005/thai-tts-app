"""
isan_converter.py - Central Thai to Isan (Northeastern Thai / Tai-Lao) Linguistic Rule Engine
Transforms standard Thai text into natural, authentic Isan speech using:
1. Compound phrase substitutions (Idioms & Multi-token collocations)
2. Lexical word mapping (Dictionary-based vocabulary)
3. Phonological consonant shift rules (ร -> ฮ, ช -> ซ)
4. Gender-aware conversational particles (จ้า/เด้อค่ะ vs เด้อครับ/ครับ)
"""

import re
from typing import List, Tuple
from pythainlp.tokenize import word_tokenize

# 1. Compound Phrases & Idioms (High-priority multi-token substitutions)
COMPOUND_PHRASES: List[Tuple[str, str]] = [
    ("ขอบคุณมากนะคะ", "ขอบใจหลายๆ เด้อจ้า"),
    ("ขอบคุณมากนะครับ", "ขอบใจหลายๆ เด้อครับ"),
    ("ขอบคุณมากค่ะ", "ขอบใจหลายๆ เด้อจ้า"),
    ("ขอบคุณมากครับ", "ขอบใจหลายๆ เด้อครับ"),
    ("ขอบคุณค่ะ", "ขอบใจเด้อจ้า"),
    ("ขอบคุณครับ", "ขอบใจเด้อครับ"),
    ("ขอบคุณมาก", "ขอบใจหลายๆ เด้อ"),
    ("ขอบคุณ", "ขอบใจหลายๆ"),
    ("ยินดีต้อนรับ", "ยินดีต้อนฮับ"),
    ("สวัสดีค่ะ", "สวัสดีจ้า"),
    ("สวัสดีครับ", "สวัสดีครับ"),
    ("ทานข้าวหรือยัง", "กินข้าวแล้วบ่"),
    ("กินข้าวหรือยัง", "กินข้าวแล้วบ่"),
    ("เป็นอย่างไรบ้าง", "เป็นจังใด๋แหน่"),
    ("เป็นยังไงบ้าง", "เป็นจั่งใด๋"),
    ("สบายดีไหม", "สบายดีบ่"),
    ("ทำอะไรอยู่", "เฮ็ดหยังอยู่"),
    ("ทำอะไร", "เฮ็ดหยัง"),
    ("ไปไหนมา", "ไปไสมา"),
    ("ไปเที่ยวไหน", "ไปเลาะไส"),
    ("ไปเที่ยว", "ไปเลาะ"),
    ("ด้วยกันไหมคะ", "นำกันบ่จ้า"),
    ("ด้วยกันไหมครับ", "นำกันบ่ครับ"),
    ("ด้วยกันไหม", "นำกันบ่"),
    ("อะไรนะ", "อีหยังเกาะ"),
    ("พูดโกหก", "ตั๋ว"),
    ("คิดถึงนะ", "คึดฮอดเด้อ"),
    ("คิดถึงมาก", "คึดฮอดหลายๆ"),
    ("คิดถึง", "คึดฮอด"),
    ("รักนะ", "ฮักเด้อ"),
    ("รักมาก", "ฮักหลายๆ"),
    ("ทะเลาะกัน", "ผิดกัน"),
    ("ตอนเย็น", "ยามแลง"),
    ("ตอนเช้า", "ยามเซ้า"),
    ("ตอนกลางวัน", "ยามเว็น"),
    ("ตอนดึก", "ยามเดิก"),
    ("พรุ่งนี้", "มื้ออื่น"),
    ("เมื่อวานนี้", "มื้อวานนี้"),
    ("เมื่อวาน", "มื้อวาน"),
    ("วันนี้", "มื้อนี้"),
    ("นิดหน่อย", "น้อยหนึ่ง"),
    ("พวกเรา", "หมู่เฮา"),
    ("พวกเขา", "ขะเจ้า"),
    ("นะคะ", "เด้อจ้า"),
    ("นะครับ", "เด้อครับ"),
    ("นะจ๊ะ", "เด้อจ้า"),
    ("หรือเปล่า", "บ่"),
    ("หรือยัง", "แล้วบ่"),
    ("ใช่ไหม", "แม่นบ่"),
    ("จริงไหม", "อีหลีบ่"),
    ("ไม่เป็นไร", "บ่เป็นหยัง"),
    ("ไม่ต้องกลัว", "บ่ต้องย่าน"),
    ("อร่อยมาก", "แซ่บหลาย"),
    ("อร่อยจริงๆ", "แซ่บอีหลี"),
    ("โรงพยาบาล", "โฮงหมอ"),
    ("โรงเรียน", "โฮงเฮียน"),
    ("โรงแรม", "โฮงแรม"),
    ("ไม่สบาย", "บ่ซำบาย"),
    ("เหนื่อยมาก", "เมื่อยหลาย"),
]

# 2. Lexical Word Mappings (Token-level substitution)
WORD_MAP = {
    # Pronouns & People
    "คุณ": "เจ้า",
    "เธอ": "เจ้า",
    "ฉัน": "ข้อย",
    "ผม": "ข้อย",
    "ดิฉัน": "ข้อย",
    "เรา": "เฮา",
    "เขา": "เพิ่น",
    "พวกเรา": "หมู่เฮา",
    "เด็ก": "เด็กน้อย",
    "เด็กๆ": "เด็กน้อย",
    "ผู้ชาย": "ผู้บ่าว",
    "ผู้หญิง": "ผู้สาว",
    "พ่อ": "อีพ่อ",
    "แม่": "อีแม่",
    "พี่": "อ้าย",
    "พี่ชาย": "อ้าย",
    "พี่สาว": "เอื้อย",
    "เพื่อน": "เสี่ยว",
    "ใคร": "ไผ",

    # Common Verbs & Actions
    "จะ": "สิ",
    "พูด": "เว้า",
    "ดู": "เบิ่ง",
    "มอง": "เบิ่ง",
    "เห็น": "เห็น",
    "กิน": "กิน",
    "ทาน": "กิน",
    "ทำ": "เฮ็ด",
    "เที่ยว": "เลาะ",
    "เดิน": "ย่าง",
    "วิ่ง": "แล่น",
    "กลับ": "เมือ",
    "กลับบ้าน": "เมือบ้าน",
    "รัก": "ฮัก",
    "รู้": "ฮู้",
    "คิด": "คึด",
    "ช่วย": "ซ่อย",
    "ช่วยเหลือ": "ซ่อย",
    "รอ": "ถ่า",
    "ชอบ": "มัก",
    "กลัว": "ย่าน",
    "โกรธ": "สูน",
    "โมโห": "สูน",
    "ชิม": "ซิม",
    "โกหก": "ตั๋ว",
    "หลอก": "ตั๋ว",
    "เหนื่อย": "เมื่อย",

    # Adjectives & Adverbs
    "อร่อย": "แซ่บ",
    "สวย": "งาม",
    "หล่อ": "หล่อ",
    "น่ารัก": "ตาฮัก",
    "มาก": "หลาย",
    "เยอะ": "หลาย",
    "จริงๆ": "อีหลี",
    "จริง": "อีหลี",
    "เร็ว": "ไว",
    "ช้า": "ซ้า",
    "ร้อน": "ฮ้อน",
    "หนาว": "หนาว",
    "สนุก": "ม่วน",
    "สนุกสนาน": "ม่วนซื่น",
    "ที่ไหน": "ไส",
    "ไหน": "ไส",
    "อะไร": "หยัง",
    "อย่างไร": "จังใด๋",
    "ยังไง": "จังใด๋",
    "ทำไม": "เป็นหยัง",
    "ใช่": "แม่น",
    "ไม่ใช่": "บ่แม่น",
    "ไม่": "บ่",

    # Objects, Places & Environments
    "บ้าน": "เฮือน",
    "ร่ม": "ฮ่ม",
    "ช้าง": "ซ้าง",
    "เงิน": "เงิน",
    "ตลาด": "ตลาด",
    "รถไฟ": "ฮดไฟ",

    # Particles & Endings
    "ด้วยกัน": "นำกัน",
    "ด้วย": "นำ",
    "ค่ะ": "จ้า",
    "คะ": "จ้า",
    "ครับ": "ครับ",
    "นะ": "เด้อ",
    "ไหม": "บ่",
    "จ้ะ": "เด้อจ้า",
    "หน่อย": "แหน่",
    "หรือ": "หรือว่า",
}

# Consonant shift patterns for tokens not explicitly in the dictionary
CONSONANT_EXCLUSIONS = {"ระบบ", "รัฐ", "รอบ", "ร่วม", "รวม"}

def _shift_consonants(token: str) -> str:
    """Applies phonological shifts (ร -> ฮ, ช -> ซ) for non-cluster Thai tokens."""
    if token in CONSONANT_EXCLUSIONS or len(token) == 0:
        return token

    # Initial ร -> ฮ (e.g. ร้อน -> ฮ้อน, รู้ -> ฮู้, รับ -> ฮับ, เรื่อง -> เฮื่อง)
    # Exclude clusters like กร, ปร, ตร, คร, บร, พร
    if token.startswith("ร") and len(token) > 1:
        return "ฮ" + token[1:]
    
    # Initial ช -> ซ (e.g. ช้อน -> ซ้อน, เช้า -> เซ้า, ชิม -> ซิม)
    if token.startswith("ช") and len(token) > 1:
        return "ซ" + token[1:]

    return token

def to_isan(text: str, gender: str = "female") -> str:
    """
    Translates standard Central Thai text into authentic Isan (Northeastern Thai).
    Supports female ('จ้า/เด้อค่ะ') and male ('เด้อครับ/ครับ') endings.
    """
    processed = text.strip()
    if not processed:
        return ""

    # Phase 1: Compound phrase substitution
    for src, dst in COMPOUND_PHRASES:
        if gender == "male":
            dst = dst.replace("จ้า", "ครับ").replace("เด้อค่ะ", "เด้อครับ")
        elif gender == "female":
            dst = dst.replace("ครับ", "จ้า")
        processed = processed.replace(src, dst)

    # Phase 2: Word-level tokenization & mapping
    tokens = word_tokenize(processed, engine="newmm")
    out_tokens = []
    for tok in tokens:
        if tok in WORD_MAP:
            replacement = WORD_MAP[tok]
            if gender == "male" and replacement in ["จ้า", "เด้อจ้า"]:
                replacement = "ครับ" if replacement == "จ้า" else "เด้อครับ"
            elif gender == "female" and replacement in ["ครับ"]:
                replacement = "จ้า"
            out_tokens.append(replacement)
        else:
            # Phase 3: Apply consonant shift rules if applicable
            out_tokens.append(_shift_consonants(tok))

    return "".join(out_tokens)

if __name__ == "__main__":
    tests = [
        "สวัสดีค่ะ วันนี้เราจะไปเที่ยวตลาดด้วยกันไหมคะ ขอบคุณมากนะคะ",
        "อาหารร้านนี้อร่อยมาก พรุ่งนี้เรามากินด้วยกันอีกนะ",
        "เด็กๆ วิ่งเล่นกันสนุกสนานมาก",
        "คุณพ่อกับคุณแม่กลับบ้านหรือยังครับ",
        "ทำอะไรอยู่ คิดถึงมากนะ สบายดีไหม"
    ]
    print("--- Testing Female Isan Translation ---")
    for t in tests:
        print("TH :", t)
        print("ISN:", to_isan(t, gender="female"))
        print()

    print("--- Testing Male Isan Translation ---")
    for t in tests:
        print("TH :", t)
        print("ISN:", to_isan(t, gender="male"))
        print()
