# 🚀 Render.com-ga Joylash Bo'yicha Qo'llanma

Ushbu botni Render.com platformasiga bepul yoki arzon narxda joylash uchun quyidagi qadamlarni bajaring:

### 1. GitHub-ga Yuklash
Loyiha fayllarini (main.py, generator.py, keys.txt, requirements.txt) o'zingizning GitHub profilingizga yangi repo (repository) ochib yuklang.

### 2. Render.com-da Yangi Loyiha Ochish
1. [Render.com](https://dashboard.render.com/) saytiga kiring va tizimga kiring.
2. **"New +"** tugmasini bosing va **"Web Service"** yoki **"Background Worker"** (tavsiya etiladi) tanlang.
3. GitHub hisobingizni ulang va bot loyihasini tanlang.

### 3. Sozlamalar (Settings)
- **Name:** `slide-bot` (ixtiyoriy)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

### 4. Atrof-muhit O'zgaruvchilari (Environment Variables)
Render-da **"Environment"** bo'limiga o'ting va quyidagi o'zgaruvchilarni qo'shing (kod ichida o'zgartirish shart emas, agar `os.getenv` ishlatsangiz):
- `BOT_TOKEN`: @BotFather dan olgan tokeningiz.
- `GEMINI_API_KEY`: Google AI Studio-dan olgan bepul kalitingiz.

### 5. Deploy
**"Create Web Service"** tugmasini bosing. Render avtomatik ravishda botni o'rnatadi va ishga tushiradi.

---
**Eslatma:** Render-ning bepul versiyasida bot ma'lum vaqt harakatsiz tursa "uxlab" qolishi mumkin. Buning oldini olish uchun **"Background Worker"** (pullik) yoki botni vaqti-vaqti bilan "uyg'otib" turadigan servisdan foydalanish tavsiya etiladi.
