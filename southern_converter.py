"""
southern_converter.py - Central Thai to Southern Thai (ภาษาใต้ / ทองแดง) Rule & Lexical Converter
Engineered by DeepSeek & Antigravity Multi-Agent Pipeline.
Transforms Central Thai into authentic, rhythmic Southern Thai using:
1. High-priority compound phrases and idioms
2. Lexical word substitution (Vocabulary & Interrogatives)
3. Conversational particles and gender markers (คับ, นิ, ตะ, เหอ, หม้าย)
"""

import re
from typing import List, Tuple
from pythainlp.tokenize import word_tokenize

# 1. Compound Phrases & Idioms (High Priority - checked first)
COMPOUND_PHRASES: List[Tuple[str, str]] = [
    ("อร่อยมากจริงๆ", "หรอยจังฮู้ชาด"),
    ("อร่อยมากครับ", "หรอยจังฮู้คับ"),
    ("อร่อยมากค่ะ", "หรอยจังฮู้นิ"),
    ("อร่อยมาก", "หรอยจังฮู้"),
    ("อร่อยจริงๆ", "หรอยแรงชาด"),
    ("อร่อย", "หรอย"),
    ("สบายดีไหมครับ", "สบายดีหม้ายคับ"),
    ("สบายดีไหมค่ะ", "สบายดีหม้ายนิ"),
    ("สบายดีไหม", "สบายดีหม้าย"),
    ("ทำอะไรอยู่ครับ", "ทำไหรอยู่คับ"),
    ("ทำอะไรอยู่ค่ะ", "ทำไหรอยู่สาวนุ้ย"),
    ("ทำอะไรอยู่", "ทำไหรอยู่"),
    ("ทำอะไร", "ทำไหร"),
    ("เป็นอย่างไรบ้าง", "เป็นพรือมั่ง"),
    ("เป็นยังไงบ้าง", "เป็นพรือมั่ง"),
    ("อย่างไร", "พันพรือ"),
    ("ยังไง", "พันพรือ"),
    ("ไปไหนมา", "ไปไหนมานิ"),
    ("ไปเที่ยวไหน", "ไปเที่ยวไหนนิ"),
    ("กลับบ้านแล้ว", "หลบบ้านแล้ว"),
    ("กลับบ้าน", "หลบบ้าน"),
    ("พูดโกหก", "ขี้ฮก"),
    ("โกหก", "ขี้ฮก"),
    ("ทะเลาะกัน", "รบกัน"),
    ("เสียงดัง", "ฉาว"),
    ("เอะอะเสียงดัง", "ฉาวโฉ"),
    ("ไม่เคย", "ไม่หอน"),
    ("ไม่เคยเลย", "ไม่หอนเลย"),
    ("พรุ่งนี้", "ตอเช้า"),
    ("เมื่อวานนี้", "แรกวา"),
    ("เมื่อวาน", "แรกวา"),
    ("ตอนเย็น", "หวันเย็น"),
    ("ตอนเช้า", "หัวเช้า"),
    ("ตอนกลางวัน", "หวันเที่ยง"),
    ("โมโหมาก", "หวิบแรง"),
    ("โกรธมาก", "หวิบแรง"),
    ("คิดถึงมาก", "คิดถึงจังฮู้"),
    ("กินข้าวหรือยัง", "กินข้าวแล้วหม้าย"),
    ("ทานข้าวหรือยัง", "กินข้าวแล้วหม้าย"),
    ("กินข้าว", "กินข้าว"),
    ("มากจริงๆ", "จังฮู้ชาด"),
    ("มากมาย", "จังหู"),
    ("สะใจมาก", "ได้แรงอก"),
    ("สะใจจริงๆ", "ได้แรงอกชาด"),
    ("ใช่ไหม", "แม่นหม้าย"),
    ("หรือเปล่า", "หม้าย"),
    ("หรือไม่", "หม้าย"),
    ("หรือยัง", "แล้วหม้าย"),
    ("ขอบคุณมากครับ", "ขอบคุณแรงๆ คับ"),
    ("ขอบคุณมากค่ะ", "ขอบคุณแรงๆ นะสาวนุ้ย"),
    ("ขอบคุณมาก", "ขอบคุณแรงๆ"),
    ("ยินดีต้อนรับ", "ยินดีต้อนรับสู"),
    ("พวกเรา", "พวกเราสู"),
]

# 2. Lexical Word Mappings (Token Level)
WORD_MAP = {
    # Pronouns & People
    "ฉัน": "นุ้ย",
    "ผม": "ผม",
    "เรา": "พวกเรา",
    "เธอ": "สู",
    "พวกเธอ": "พวกสู",
    "พี่ชาย": "พี่บ่าว",
    "น้องสาว": "สาวนุ้ย",
    "แฟน": "แฟน",
    "พ่อ": "ป๋า",
    "แม่": "แม่",

    # Verbs & Actions
    "พูด": "แหลง",
    "คุย": "แหลง",
    "บอก": "บอก",
    "ดู": "แล",
    "มอง": "แล",
    "กลับ": "หลบ",
    "โกรธ": "หวิบ",
    "โมโห": "หวิบ",
    "วิ่ง": "แล่น",
    "เดิน": "เดิน",
    "ขี้เหนียว": "ขี้ชิด",
    "ตระหนี่": "ขี้ชิด",

    # Nouns & Fruits/Objects
    "มะละกอ": "ลอกอ",
    "สับปะรด": "ยานัด",
    "ฝรั่ง": "ชมพู่",
    "ทอดมัน": "ปลาคั่ว",

    # Interrogatives & Quantifiers
    "อะไร": "ไอ้ไหร",
    "ทำไม": "ไซร",
    "ที่ไหน": "แถวไหน",
    "เยอะ": "ลุย",
    "มาก": "แรง",
    "จริง": "ชาด",
}

def to_southern(text: str, gender: str = "female") -> str:
    """
    Transforms Central Thai text into natural Southern Thai dialogue.
    """
    if not text or not text.strip():
        return text

    converted = text

    # Phase 1: High priority compound substitutions
    for central, southern in COMPOUND_PHRASES:
        converted = converted.replace(central, southern)

    # Phase 2: Tokenize and map individual vocabulary
    tokens = word_tokenize(converted, engine="newmm")
    mapped_tokens = []
    for tok in tokens:
        if tok in WORD_MAP:
            mapped_tokens.append(WORD_MAP[tok])
        else:
            mapped_tokens.append(tok)

    result = "".join(mapped_tokens)

    # Phase 3: Conversational particles & Gender adjustments
    # Southern gender particles:
    # Male: คับ / พี่บ่าว
    # Female: นิ / ตะ / สาวนุ้ย
    if gender == "male":
        result = re.sub(r'ครับ\b', 'คับ', result)
        result = re.sub(r'ค่ะ|คะ', 'คับ', result)
        if not any(result.endswith(p) for p in ['คับ', 'หม้าย', 'นิ', 'ตะ', 'ฮู้', 'ชาด', 'แรง']):
            result += " คับ"
    else:
        result = re.sub(r'ค่ะ|คะ', 'นิ', result)
        result = re.sub(r'ครับ\b', 'นิ', result)
        if not any(result.endswith(p) for p in ['นิ', 'ตะ', 'หม้าย', 'ฮู้', 'เหอ', 'ชาด', 'แรง', 'สาวนุ้ย']):
            result += " นิ"

    # Clean double spaces
    result = re.sub(r'\s+', ' ', result).strip()
    return result
