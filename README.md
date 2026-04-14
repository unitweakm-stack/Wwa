# 🎓 Institutlar uchun Aqlli Slayd Yaratuvchi Telegram Bot (V4)

Ushbu bot **Google Gemini AI** (bepul versiyasi) orqali institut talabalari va o'qituvchilari uchun mukammal va aqlli slaydlar yaratib beradi. Bot xavfsizlik uchun murakkab API kalit (KEY) tizimi bilan jihozlangan.

## ✨ Asosiy Xususiyatlar
- **Bepul AI (Gemini):** Slaydlar mazmuni Google Gemini AI orqali mutlaqo bepul va aqlli tarzda yaratiladi.
- **500 ta Murakkab Kalit:** Loyiha ichida 500 ta taxmin qilib bo'lmaydigan kalitlar mavjud (`keys.txt`).
- **Limit Tizimi:** Har bir kalit foydalanuvchiga faqat **2 ta slayd** yaratish imkonini beradi.
- **Turli Dizaynlar:** Akademik, Modern va Dark (Tungi) rejimlar.
- **Format:** Slaydlar PPTX formatida yaratiladi.

## 🚀 O'rnatish va Ishga Tushirish

1. **Kutubxonalarni o'rnating:**
   ```bash
   pip install python-telegram-bot python-pptx google-generativeai
   ```

2. **API Kalitlarni sozlang:**
   `main.py` faylini oching va quyidagilarni kiriting:
   - `BOT_TOKEN`: @BotFather dan olgan tokeningiz.
   - `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/app/apikey) dan olingan bepul kalit.

3. **Botni ishga tushiring:**
   ```bash
   python main.py
   ```

## 🔑 API Kalitlar Tizimi
Barcha 500 ta murakkab kalit `keys.txt` faylida saqlangan. Har bir kalit 2 ta slayd uchun amal qiladi. Agar yangi kalitlar kerak bo'lsa, `generate_keys.py` skriptini ishga tushiring.

## 🛠 Texnologiyalar
- **Python 3.x**
- **Google Gemini AI API** (Bepul mazmun yaratish uchun)
- **python-telegram-bot**
- **python-pptx**

## 📝 Muallif
Ushbu loyiha institutlar uchun eng zamonaviy va bepul AI yechimi sifatida tayyorlandi.
