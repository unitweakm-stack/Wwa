import os
import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from generator import SlideGenerator
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Kalitlarni yuklash
def load_keys():
    try:
        with open("keys.txt", "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        logger.warning("keys.txt topilmadi. Kalitlar yuklanmadi.")
        return []

VALID_KEYS = load_keys()

# TOKENS (Environment variables or default placeholder)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# Foydalanuvchi holatini saqlash
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"authenticated": False, "step": "auth", "slides_count": 0}
    
    await update.message.reply_text(
        "🎓 Institutlar uchun aqlli slayd yaratuvchi botga xush kelibsiz!\n\n"
        "Botni ishlatish uchun maxsus kalitni (KEY) kiriting:"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"authenticated": False, "step": "auth", "slides_count": 0}

    # Kalitni tekshirish
    if not user_data[user_id]["authenticated"]:
        if text in VALID_KEYS:
            user_data[user_id]["authenticated"] = True
            user_data[user_id]["step"] = "topic"
            await update.message.reply_text(
                "✅ Kalit tasdiqlandi! Siz 2 ta aqlli slayd yaratish huquqiga ega bo'ldingiz.\n"
                "Endi slayd mavzusini yuboring:"
            )
        else:
            await update.message.reply_text("❌ Noto'g'ri kalit! Iltimos, to'g'ri kalitni kiriting.")
        return

    # Mavzuni qabul qilish
    if user_data[user_id]["step"] == "topic":
        user_data[user_id]["topic"] = text
        user_data[user_id]["step"] = "theme"
        
        keyboard = [
            [InlineKeyboardButton("Akademik (Oddiy)", callback_data='akademik')],
            [InlineKeyboardButton("Modern (Rangli)", callback_data='modern')],
            [InlineKeyboardButton("Dark (Tungi rejim)", callback_data='dark')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Mavzu: {text}\n\nEndi slayd dizaynini tanlang:",
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    theme = query.data
    
    await query.answer()
    await query.edit_message_text(text=f"Tanlangan dizayn: {theme.capitalize()}\nGemini AI slayd mazmunini tayyorlamoqda, iltimos kuting...")

    topic = user_data[user_id].get("topic", "Mavzu")
    
    # Gemini AI orqali mazmun yaratish
    generator = SlideGenerator(api_key=GEMINI_API_KEY)
    content_list = generator.generate_content_with_ai(topic)
    
    pptx_file = f"slide_{user_id}.pptx"
    generator.create_presentation(topic, content_list, theme, pptx_file)
    
    try:
        with open(pptx_file, 'rb') as doc:
            await context.bot.send_document(
                chat_id=user_id,
                document=doc,
                filename=f"{topic}.pptx",
                caption=f"✅ {topic} mavzusidagi aqlli slaydingiz tayyor!\n\nGemini AI tomonidan yaratildi."
            )
        
        # Slaydlar sonini oshirish
        user_data[user_id]["slides_count"] += 1
        
        # 2 ta slayd bo'ldimi?
        if user_data[user_id]["slides_count"] >= 2:
            user_data[user_id]["authenticated"] = False
            user_data[user_id]["slides_count"] = 0
            user_data[user_id]["step"] = "auth"
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Sizning 2 ta slayd yaratish limitungiz tugadi.\nDavom etish uchun yangi kalit (KEY) kiriting:"
            )
        else:
            user_data[user_id]["step"] = "topic"
            await context.bot.send_message(
                chat_id=user_id,
                text=f"Siz yana 1 ta slayd yaratishingiz mumkin.\nKeyingi slayd mavzusini yuboring:"
            )
            
    except Exception as e:
        await query.message.reply_text(f"Xatolik yuz berdi: {e}")
    finally:
        if os.path.exists(pptx_file):
            os.remove(pptx_file)

if __name__ == '__main__':
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("BOT_TOKEN o'rnatilmagan! Iltimos, Render-da BOT_TOKEN environment variable-ni o'rnating.")
        sys.exit(1)
    
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("Bot ishga tushdi...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
        sys.exit(1)
