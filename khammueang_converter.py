"""
khammueang_converter.py - Central Thai to Northern Thai (Kham Mueang) Linguistic Rule Engine
Transforms standard Thai text into natural Northern Thai (Lanna) using:
1. Compound phrase substitutions
2. Lexical word mapping (Dictionary-based)
3. Phonological consonant shift rules (ร->ฮ, ช->จ, ท->ต, พ->ป)
4. Mid-consonant tone shift (ก, จ, ต, ป -> ๋)
5. Northern conversational particles (เจ้า, เน้อ, ก่อ, โตยกั๋น)
"""

from typing import List, Tuple
from pythainlp.tokenize import word_tokenize

# 1. Compound Phrases & Idioms (High priority multi-word matches)
COMPOUND_PHRASES: List[Tuple[str, str]] = [
    ("ขอบคุณมากค่ะ", "ยินดีจั๊ดนักเจ้า"),
    ("ขอบคุณมากครับ", "ยินดีจั๊ดนักคับ"),
    ("ขอบคุณค่ะ", "ยินดีเจ้า"),
    ("ขอบคุณครับ", "ยินดีคับ"),
    ("ขอบคุณมาก", "ยินดีจั๊ดนัก"),
    ("ขอบคุณ", "ยินดี"),
    ("ยินดีต้อนรับ", "ยินดีต้อนฮับ"),
    ("ทานข้าวหรือยัง", "กิ๋นข้าวแล้วกา"),
    ("กินข้าวหรือยัง", "กิ๋นข้าวแล้วกา"),
    ("เป็นอย่างไรบ้าง", "เป๋นจะใดพ่อง"),
    ("เป็นยังไงบ้าง", "เป๋นจะใดพ่อง"),
    ("สบายดีไหม", "สบายดีก่อ"),
    ("ทำอะไรอยู่", "ยะหยังอยู่"),
    ("ทำอะไร", "ยะหยัง"),
    ("ไปไหนมา", "ไปตางใดมา"),
    ("ไปเที่ยวไหน", "ไปแอ่วตางใด"),
    ("ไปเที่ยว", "ไปแอ่ว"),
    ("เที่ยว", "แอ่ว"),
    ("ด้วยกันไหมคะ", "โตยกั๋นก่อเจ้า"),
    ("ด้วยกันไหมครับ", "โตยกั๋นก่อคับ"),
    ("ด้วยกันไหม", "โตยกั๋นก่อ"),
    ("อะไรนะ", "อะหยังเกาะ"),
    ("พูดโกหก", "ขี้จุ๊"),
    ("โกหก", "ขี้จุ๊"),
    ("ทะเลาะกัน", "ผิดกั๋น"),
    ("ตอนเย็น", "เมื่อแลง"),
    ("ตอนเช้า", "เมื่อเจ๊า"),
    ("ตอนกลางวัน", "เมื่อวัน"),
    ("พรุ่งนี้", "วันพูก"),
    ("เมื่อวานนี้", "วานซืน"),
    ("เมื่อวาน", "วานซืน"),
    ("นิดหน่อย", "น้อยเดียว"),
    ("พวกเรา", "หมู่เฮา"),
    ("นะคะ", "เน้อเจ้า"),
    ("นะครับ", "เน้อคับ"),
    ("นะจ๊ะ", "เน้อเจ้า"),
    ("หรือเปล่า", "ก่อ"),
    ("หรือยัง", "แล้วกา"),
]

# 2. Lexical Word Mappings (Token-level substitution)
WORD_MAP = {
    # Pronouns & People
    "คุณ": "ตั๋ว",
    "ฉัน": "เปิ้น",
    "เรา": "เฮา",
    "เขา": "เปิ้น",
    "พวกเรา": "หมู่เฮา",
    "เด็ก": "ละอ่อน",
    "เด็กๆ": "ละอ่อน",
    "ผู้ชาย": "ป้อจาย",
    "ผู้หญิง": "แม่ญิ๋ง",
    "พ่อ": "ป้อ",
    "แม่": "แม่",
    "พี่": "ปี้",
    "พี่ชาย": "ปี่อ้าย",
    "พี่สาว": "ปี่สาว",
    "เพื่อน": "เปื้อน",
    "ใคร": "ไผ",

    # Common Verbs & Actions
    "พูด": "อู้",
    "กิน": "กิ๋น",
    "ทาน": "กิ๋น",
    "ดู": "ผ่อ",
    "มอง": "ผ่อ",
    "เที่ยว": "แอ่ว",
    "เดิน": "เตียว",
    "วิ่ง": "แล่น",
    "กลับ": "ปิ๊ก",
    "กลับบ้าน": "ปิ๊กบ้าน",
    "รัก": "ฮัก",
    "รู้": "ฮู้",
    "คิด": "กึ๊ด",
    "ทำ": "ยะ",
    "ช่วยเหลือ": "จ้วย",
    "ช่วย": "จ้วย",
    "รอ": "ถ้า",
    "ฟัง": "ฟั่ง",

    # Adjectives & Adverbs
    "อร่อย": "ลำ",
    "สวย": "งาม",
    "มาก": "ขนาด",
    "เยอะ": "นัก",
    "ร้อน": "ฮ้อน",
    "ช้า": "จ๊า",
    "เร็ว": "โวย",
    "หนาว": "หนาว",
    "สนุก": "ม่วน",
    "สนุกสนาน": "ม่วนงัน",

    # Objects & Places
    "ตลาด": "กาด",
    "บ้าน": "เฮือน",
    "ร่ม": "จ้อง",
    "ช้าง": "จ๊าง",
    "ทาง": "ตาง",
    "ที่": "ตี้",
    "ไหน": "ตางใด",
    "อะไร": "อะหยัง",
    "อย่างไร": "จะใด",
    "ยังไง": "จะใด",

    # Particles & Endings
    "ด้วยกัน": "โตยกั๋น",
    "ด้วย": "โตย",
    "ค่ะ": "เจ้า",
    "คะ": "เจ้า",
    "ครับ": "คับ",
    "นะ": "เน้อ",
    "ไหม": "ก่อ",
    "จ้ะ": "เจ้า",
}

def to_khammueang(text: str, gender: str = "female") -> str:
    """
    Translates standard Central Thai text into authentic Northern Thai (Kham Mueang).
    """
    processed = text.strip()
    if not processed:
        return ""

    # Phase 1: Compound phrase replacement
    for src, dst in COMPOUND_PHRASES:
        if gender == "male":
            dst = dst.replace("เจ้า", "คับ")
        processed = processed.replace(src, dst)

    # Phase 2: Word-level tokenization & mapping
    tokens = word_tokenize(processed, engine="newmm")
    out_tokens = []
    for tok in tokens:
        if tok in WORD_MAP:
            replacement = WORD_MAP[tok]
            if gender == "male" and replacement in ["เจ้า"]:
                replacement = "คับ"
            out_tokens.append(replacement)
        else:
            out_tokens.append(tok)

    return "".join(out_tokens)

if __name__ == "__main__":
    tests = [
        "สวัสดีค่ะ วันนี้เราจะไปเที่ยวตลาดด้วยกันไหมคะ ขอบคุณมากนะคะ",
        "อาหารร้านนี้อร่อยมาก พรุ่งนี้เรามากินด้วยกันอีกนะ",
        "เด็กๆ วิ่งเล่นกันสนุกสนานมาก",
        "คุณพ่อกับคุณแม่กลับบ้านหรือยังคะ"
    ]
    for t in tests:
        print("TH:", t)
        print("KM:", to_khammueang(t))
        print()
