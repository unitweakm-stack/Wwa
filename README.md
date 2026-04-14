# Telegram OCR Bot (Key Management System bilan)

Ushbu bot Telegram orqali yuborilgan rasmlardagi matnlarni aniqlash (OCR) va 500 ta bir martalik, 30 kunlik kalitlar (key) tizimi bilan ishlaydi.

## Xususiyatlari
- **OCR Integration**: [OCR.Space](https://ocr.space/ocrapi) API orqali rasmdan matnni aniqlash.
- **Key Management**: 500 ta o'rnatilgan kalitlar.
- **Subscription System**: Faollashtirilgan kundan boshlab 30 kunlik obuna.
- **Single File**: Barcha asosiy mantiq `main.py` ichida.

## O'rnatish

1. Loyihani yuklab oling:
```bash
git clone https://github.com/username/telegram_ocr_bot.git
cd telegram_ocr_bot
```

2. Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

3. `.env` faylini yarating va quyidagi ma'lumotlarni kiriting:
```env
BOT_TOKEN=Sizning_Telegram_Bot_Tokeningiz
OCR_SPACE_API_KEY=Sizning_OCR_Space_API_Kalitingiz
DEFAULT_LANG=tur
```

## Ishga tushirish
```bash
python main.py
```

## Buyruqlar
- `/start` - Botni ishga tushirish va obuna holatini tekshirish.
- `/activate KEY` - Kalitni faollashtirish (masalan: `/activate A5B4613A86E8`).

## Kalitlar ro'yxati
Barcha 500 ta kalit `keys_list.txt` faylida keltirilgan.
