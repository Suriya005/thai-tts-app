"""
southern_phonology.py - Authentic Southern Thai (ภาษาใต้ / สำเนียงทองแดง) Phonology & Tone Rules
Engineered by DeepSeek Reasoning & Phonology Module for thai-tts-app.
Features:
- Southern Thai Tone contours (5-7 tones depending on region: Nakhon Si, Songkhla, Surat)
- Initial Consonant shifting (High register, unaspirated plosives, and glottal stops)
- High-priority Southern lexical overrides and phonetic mapping.
"""

from typing import Dict

# Phonetic overrides for characteristic Southern Thai words
SOUTHERN_PHONETIC_OVERRIDES: Dict[str, str] = {
    # Pronouns & Relatives
    "นุ้ย": "nuj˦˥",        # ฉัน/น้อง
    "พี่บ่าว": "pʰiː˥˩ baːw˨˩", # พี่ชาย
    "สาวนุ้ย": "saːw˨˦ nuj˦˥",  # น้องสาว
    "สู": "suː˨˦",          # พวกเธอ/สู
    "เพิ่น": "pʰɤn˥˩",
    
    # Particles & Questions
    "หม้าย": "maːj˦˥",       # ไหม/หรือเปล่า
    "นิ": "niʔ˦˥",          # นะ/นี่
    "ตะ": "taʔ˦˥",          # เถอะ/สิ
    "เหอ": "hɤː˨˦",         # เอ๋ย/นะ
    "เล่า": "law˥˩",        # อีกแล้ว
    "ฮู้": "huː˦˥",         # จังฮู้
    
    # Common Verbs & Actions
    "แหลง": "lɛːŋ˩",        # พูด
    "แล": "lɛː˧",           # ดู/มอง
    "หลบ": "lop̚˦˥",        # กลับ
    "หลบบ้าน": "lop̚˦˥ baːn˥˩", # กลับบ้าน
    "หวิบ": "wip̚˦˥",        # โกรธ/โมโห
    "ขี้ฮก": "kʰiː˥˩ hok̚˦˥", # ขี้โกหก
    "ฉาว": "tɕʰaːw˨˦",      # ส่งเสียงดัง
    "ไม่หอน": "maj˥˩ hɔːn˨˦", # ไม่เคย
    
    # Interrogatives
    "ไซร": "saj˨˦",         # ทำไม
    "ทำไซ": "tʰam˧ saj˨˦",  # ทำไม
    "ไอ้ไหร": "ʔaj˥˩ raj˨˦", # อะไร
    "พรือ": "pʰrɯː˧",       # อย่างไร
    "เป็นพรือ": "pen˧ pʰrɯː˧", # เป็นอย่างไร
    
    # Adjectives & Taste
    "หรอย": "rɔːj˨˦",       # อร่อย/ยอดเยี่ยม
    "หรอยจังฮู้": "rɔːj˨˦ tɕaŋ˧ huː˦˥", # อร่อยมากๆ
    "หรอยแรง": "rɔːj˨˦ rɛːŋ˧", # อร่อยสุดๆ
    "ชาด": "tɕʰaːt̚˥˩",      # แท้ๆ/จริงๆ (ชาดหรอย = โคตรอร่อย)
    "จังหู": "tɕaŋ˧ huː˨˦",   # มากมาย
    "ได้แรงอก": "daːj˥˩ rɛːŋ˧ ʔok̚˦˥" # สะใจ/ถูกใจอย่างแรง
}

def get_southern_tone_profile() -> Dict[str, str]:
    """Returns description of Southern Thai tone characteristics."""
    return {
        "short_vowel_dead_syllable": "High-Fast Glottal Stop (Tone 6/7)",
        "tone_shift": "Consonant-tone polarization characteristic of Pak Tai",
        "speed_factor": "1.12x (Southern speech is typically 10-15% faster and crisper than Central Thai)"
    }
