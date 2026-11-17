# Thai TTS Benchmark & Testing Studio (สตูดิโอทดสอบสังเคราะห์เสียงพูดภาษาไทย)

แอปพลิเคชันเว็บแบบ Interactive สำหรับทดสอบ ฟังเสียง และเปรียบเทียบโมเดลสังเคราะห์เสียงพูดภาษาไทย (Thai Text-to-Speech) คุณภาพสูงหลากหลายสถาปัตยกรรม (VITS, ONNX, Kokoro, Meta MMS Dialects, Edge Neural) แบบตัวต่อตัว (Head-to-Head Comparison)

---

## 🌟 ฟีเจอร์หลัก (Key Features)

1. **โหมดทดสอบรายโมเดล (Playground Mode):**
   - เลือกระบบเสียง ปรับสปีด (Speed), ความดัง (Volume), และ Noise Scale (ความสดธรรมชาติของเสียง)
   - เครื่องเล่นเสียง HTML5 ในตัว พร้อมบอก Latency (มิลลิวินาที), ความยาวเสียง และขนาดไฟล์
   - ปุ่มดาวน์โหลดไฟล์เสียง (.wav / .mp3) ได้ทันที

2. **ระบบเสียงพากย์สำเนียงถิ่นไทย (Regional Thai Dialects):**
   - 🌸 **ภาษาเหนือ (คำเมือง / ล้านนา):** ขับเคลื่อนด้วยโมเดล `facebook/mms-tts-nod` (VITS 16kHz) สำเนียงเหนือแท้
   - 🌾 **ภาษาอีสาน (Isan / Lao Phonology):** ขับเคลื่อนด้วย `facebook/mms-tts-lao` ผสานกับ **Thai-to-Lao Transliteration Bridge** แปลงอักษรไทยเป็นลาวแบบเรียลไทม์ ทำให้สังเคราะห์เสียงเว้าอีสานได้อย่างแม่นยำ
   - 🏛️ **ภาษาไทยกลาง (MMS):** โมเดล `facebook/mms-tts-tha` สำหรับเทียบเคียง

3. **โหมดเปรียบเทียบพร้อมกัน (Head-to-Head Compare Matrix):**
   - พิมพ์ 1 ประโยค -> กดปุ่มเดียวสังเคราะห์เปรียบเทียบพร้อมกันแบบ A/B/C Testing
   - ระบบ Auto-Pause หยุดเสียงอื่นอัตโนมัติเมื่อกดฟังเสียงใดเสียงหนึ่ง เพื่อให้เทียบความต่างของสำเนียงได้ชัดเจนที่สุด

4. **ชุดประโยคทดสอบความท้าทายของภาษาไทย (Linguistic Presets):**
   - 🗣️ **การออกเสียงพยัญชนะ "ร" และ "ล":** ตรวจสอบการกระดกลิ้นและความชัดเจน
   - 🔢 **ตัวเลข วันที่ และเวลา:** ทดสอบการแปลงเลขอารบิก จุดทศนิยม และหน่วยเวลา
   - 🌐 **คำทับศัพท์ภาษาอังกฤษ (Code-Switching):** ทดสอบการอ่านคำผสม เช่น meeting, status, presentation
   - 🎙️ **พอดแคสต์/สารคดี (Narrative):** ประเมินจังหวะการเล่าเรื่องต่อเนื่อง
   - 🔁 **ไม้ยมก (ๆ) และคำซ้ำ:** ทดสอบการอ่านซ้ำคำอัตโนมัติ
   - 🌸 **สำเนียงถิ่น 4 ภาค:** พรีเซ็ตประโยคเหนือ, อีสาน, ใต้, สุพรรณ พร้อมระบบสลับโมเดลอัตโนมัติ

5. **คู่มือวิจัยเชิงลึก (Deep Learning Guide):**
   - สรุปรายละเอียดโมเดลใหญ่ OmniVoice Thai (~4.4GB), F5-TTS-THAI (Flow Matching) และ JaiTTS-v1.0 (VoxCPM SOTA 2026) พร้อมโค้ดตัวอย่างใน Python

---

## 🎧 โมเดลที่พร้อมใช้งานในระบบ (Pre-loaded Models)

| โมเดล / เครื่องยนต์ | สถาปัตยกรรม | เสียงที่มีให้เลือก | จุดเด่น | การทำงาน |
|---|---|---|---|---|
| **Meta MMS Dialects** | VITS (Transformers) | `mms_nod` (เหนือ), `mms_isan` (อีสาน), `mms_tha` (กลาง) | สำเนียงถิ่นล้านนาและเว้าอีสานแท้ ไม่กินการ์ดจอ | รันบน CPU/GPU ในเครื่อง (ออฟไลน์) |
| **VachanaTTS** | VITS (ONNX / Piper) | `th_f_1`, `th_f_2`, `th_m_1`, `th_m_2` | สำเนียงไทยชัดเจนมาก เสียงผู้ชาย `th_m_1` และหญิง `th_f_2` CER ต่ำมาก | รันบน CPU/GPU ในเครื่อง (ออฟไลน์) |
| **PyThaiTTS** | FastThaiG2P (Kokoro-82M) | `fastthaig2p` (thai_som) | สถาปัตยกรรม Kokoro ใหม่ พร้อม G2P จัดการเลขอารบิกและคำอังกฤษในตัว | รันบนเครื่อง (ออฟไลน์) |
| **PyThaiTTS** | MakHam Paradee | `makham_paradee` | ขนาดเล็กมาก (~8MB) สปีดเร็วระดับ Realtime เหมาะกับอุปกรณ์พกพา | รันบนเครื่อง (ออฟไลน์) |
| **PyThaiTTS** | Lunarlist ONNX | `lunarlist_onnx` | โมเดล ONNX น้ำหนักเบาจาก PyThaiNLP | รันบนเครื่อง (ออฟไลน์) |
| **Edge Neural** | Microsoft Neural HD | `Premwadee` (หญิง), `Niwat` (ชาย) | ใช้เป็นเกณฑ์มาตรฐานวัดเปรียบเทียบ (Commercial Baseline) | ต้องต่อเน็ต |
| **Google TTS** | Standard | `th` | ใช้เป็นเกณฑ์เปรียบเทียบวิวัฒนาการจาก TTS รุ่นเดิม | ต้องต่อเน็ต |

---

## 🚀 วิธีติดตั้งและเปิดใช้งาน (Installation & Setup)

### 1. โคลน Repository
```bash
git clone https://github.com/your-username/thai-tts-app.git
cd thai-tts-app
```

### 2. สร้าง Virtual Environment และติดตั้ง Dependencies
```bash
# แนะนำ Python 3.10 หรือ 3.11
python -m venv .venv
.\.venv\Scripts\activate

# ติดตั้งแพ็กเกจ
pip install -r requirements.txt
```

### 3. เปิดใช้งานแอพพลิเคชัน
#### วิธีที่ 1: ดับเบิลคลิกไฟล์ (Windows)
ดับเบิลคลิกไฟล์ **`start_app.bat`** ระบบจะรันเซิร์ฟเวอร์และเปิดหน้าเว็บขึ้นมาบนเบราว์เซอร์ให้อัตโนมัติที่ `http://127.0.0.1:8765`

#### วิธีที่ 2: รันผ่าน Terminal
```powershell
python server.py
```
แล้วเปิดเบราว์เซอร์ไปที่: **http://127.0.0.1:8765**

---

## 🛠️ โครงสร้างโปรเจกต์ (Project Structure)

```
thai-tts-app/
├── dialect_engine.py    # ตัวจัดการโมเดล Meta MMS และ Thai-to-Lao Transliteration Bridge
├── server.py            # FastAPI Server สำหรับจัดการโมเดลและ API การสังเคราะห์เสียง
├── static/              # เว็บแอปพลิเคชัน UI (Tailwind CSS, Lucide icons, Audio player)
│   ├── index.html       # หน้าเว็บหลัก Responsive & Dark mode
│   ├── app.js           # โลจิกฝั่งผู้ใช้ จัดการเครื่องเล่นเสียงและโหมด Compare Matrix
│   └── style.css        # สไตล์และแอนิเมชัน
├── output/              # โฟลเดอร์เก็บไฟล์เสียงที่สังเคราะห์ (.wav / .mp3)
├── requirements.txt     # รายการ Dependencies ทั้งหมด
├── start_app.bat        # สคริปต์คลิกเดียวรันแอพสำหรับ Windows
└── README.md            # เอกสารประกอบการใช้งาน
```

---

## 📄 License
MIT License
