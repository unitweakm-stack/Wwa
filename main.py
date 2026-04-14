import os
import io
import re
import json
import asyncio
import threading
import urllib.parse
import urllib.request
import logging
from datetime import datetime, timedelta
from flask import Flask

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import Application, MessageHandler, ContextTypes, filters, CommandHandler

# --- WEB SERVER (Render 24/7 uchun) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7! Status: OK"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Flask serveri {port}-portda ishga tushmoqda...")
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURATSIYA ---
OCR_API_URL = "https://api.ocr.space/parse/image"
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "tur").strip().lower() or "tur"
USER_DATA_FILE = "user_subscriptions.json"
ADMIN_USERNAME = "@backeer"

# --- 500 TA KALIT RO'YXATI ---
VALID_KEYS = [
    "A5B4613A86E8", "7540D41C7B6B", "87FFC0BE396E", "9F329F650BE2", "D4F3A97A4B07", "344238F4F294", "82602FD81E23", "D665180362C9", "8DF35F615ECC", "02F3EC030EBC",
    "9F85F2240B03", "16419417ECAD", "3D590AD7F57C", "35AEA80B0B3D", "0F951227709A", "67DAEE9D662E", "8174A1A6CB21", "6D9E8F8C8C68", "3A92D43CAA34", "9981AC38A085",
    "139CC4ABFA96", "29A117C2D0EF", "83FB669B5114", "72025FF76CEC", "9A56A8F677A0", "1F3A655F5080", "4DBEAC596ED4", "FB94EBBDF296", "662532D6F3A1", "07027B8F60B5",
    "9D3D0AA1DF61", "767CC4752D7B", "94FC3E00DF0D", "6588DF54694F", "B2953677965F", "8D6ACA7451BD", "02683F550FBA", "E47CDDF7DDDC", "FFAEDFB2BEE7", "DDD40D758AE4",
    "C9DF13FF3D2F", "58E5C8FD743E", "F70F7D5D497B", "158966B10B63", "3E911F6DE686", "149CFD1D8B57", "2BC1AB6ECA01", "BBB92021D06F", "83A021F8A8A7", "2C46EF7A55AC",
    "BB3BEAC25F52", "417644E2BAB9", "5AF14EED4C72", "1F66FC7AD6DF", "605639163B01", "9B015BDDB792", "210E74C21F36", "C21024879975", "1844CB4FFC7C", "BCC66849B26D",
    "EE35513E8E62", "1952DB8669EE", "53038B265BB0", "37C9FCDAF65A", "2F3C818AA6AE", "25C42D0EAC14", "7FA00BB95B0E", "DBC01726D522", "FDC48F8CD79A", "267797A0DA3A",
    "F0C552AC0CCC", "6F9BE9DD18E1", "0E9B92312518", "33217B051E8C", "D47D8200F781", "CDAD6E55ADEB", "816DC0E91827", "0CC63AFFD9E2", "DC7D2D61C6E1", "D4A657B28E54",
    "866744D78779", "F49F33EA877E", "5B21EB8DB244", "7C7B678126C5", "775D0709E10F", "206148326175", "1D6C0BE1AE56", "504A31511074", "379DB6FDDC62", "C5F251CEF846",
    "98BF70096804", "228005D2B8EC", "D7E6BAC634B6", "286992B5BB14", "3F78DC678F8C", "0854B5C5E631", "54ACBD4B85EF", "E9EF299B6427", "F86E54C27D70", "DFB3279A1C6C",
    "34D201D4B816", "80C5C4598FB3", "63B140618880", "5F45F93A01A0", "3AADA5DDCAEB", "5013DC8F4812", "C375E8F038CA", "5EF6BB3F5E08", "7FE7AE6F549C", "E0B7855025CB",
    "215281DE2F5B", "7249E950614C", "922A6EC3CD00", "04C19F4B55EB", "D6CAB39F17FD", "9146976568CE", "DD84F2C1B25E", "73159579F16F", "6BC31DAC7339", "1D406BD283E9",
    "952AD11BECEA", "831BD1809F23", "9A27A02E4026", "24D1101B08F7", "E83F56ECA346", "65056F98E8B5", "335CA3694369", "4C8E7764945F", "E82E67127A78", "7EEB335C7873",
    "0EA0A7BE4ABC", "DE29346CF419", "B3FDC572A63C", "3DECC653D312", "B4094F11739D", "1149A663C1FD", "200A903EF7FB", "53263119551E", "3722DBBF48B8", "F7D4A55C0305",
    "228333ED6E56", "7F4EEDE4D6B5", "6905EA7470FE", "BEC5AA00013F", "9A766B8F65A0", "ADE8BD651D84", "89DAFCF4137D", "A7B0F844FF7B", "BF8EAEED4781", "C92915E52FB2",
    "CCF4B72CB5D1", "17E27A307CFC", "D8EE6A7CE061", "1E4FA187CE36", "5DC9698D8290", "EE41FD0A9464", "3581A9207C0F", "ED6C1DECB952", "EB46985D5F25", "B8480AA6B935",
    "2D6C5DBB939C", "B0B64823514C", "CEDD6BFE7F32", "F19A06517ECC", "37205990953B", "F7D523D941E0", "AEF8BFDD0CC7", "0C8A0EE58240", "21FA04B7AEC1", "98B7DEBF42A0",
    "D4B4771942AB", "AA361E8CDAA6", "C95D8F2C3E4A", "86B73CCEC7D5", "0ED79BAC3952", "443F765C7098", "1DDF4EB52F28", "6034F7FE4825", "AF64843D2BF7", "8979AB788803",
    "9E96A0885054", "23303F92F269", "F7FA8CDBA2A1", "6207A9EEE8F4", "A4238E92CC73", "FE2527A6642E", "6DADA7AD3FD5", "9BE604891C81", "D9F8A4AC9B29", "CCFF165FA07A",
    "4F5EE3E5A493", "C2FF61010C82", "6A3F9B83B704", "070F242FEF09", "B7E1A1AAEC14", "2A0467D87DFB", "3678D37B13BF", "1E88DB0DFA49", "DDF1A39799CF", "CBF73DD9B9E4",
    "4228ACA11873", "E5314DB684F0", "1D6E436B0400", "2E118C8D69E1", "40D0CF3935F0", "82F4780D148A", "0273513437C8", "643FDD802BD1", "E211B7783DDD", "A0460D3F47BE",
    "311DD0F8528E", "50BDF4812B43", "B88D0020C968", "954EB82F1EAE", "FFE44F60959D", "55E5C05B301A", "E6C8C6E30790", "37E2520EFB4A", "7DB308ED52B5", "2D4D4F9E61B6",
    "F1F2FD0E9CF0", "46B72383E31E", "D300F8C0D6F1", "B492515292B0", "27F74BC476EE", "7E4F75E24595", "A6A489D54F78", "65C4AA65C2F2", "1D3A1E6B2D33", "1BBD7BDD2D7C",
    "42F5976D3D09", "B0DEA1A4F676", "1D3C462147B5", "533E8E75E60B", "E8BA37DDEFCA", "716CBBE9FBF5", "B81C728A284E", "AEA715F3FD96", "601DB9B48597", "875E5E327B66",
    "2BF5A673A97E", "D8BF018B9256", "28C9A3A2B5CC", "EAED56CB1DB6", "1BCCA077AF22", "EB3040C4424E", "FDDF019646FD", "75986FCFAB03", "5A2C06249386", "FA9D1C107079",
    "2932E1FF53E6", "7AD69B427272", "B5872BB2A606", "87BD17311E1C", "5B90FD738C0F", "68E79B4ED8D1", "3726DB340D03", "CC0938BD664F", "BE88A8D83E4D", "F46529FF30AC",
    "206709BDFA80", "42E0F23846A8", "59D163814216", "3B73FD6C9032", "250F1C0216DB", "EDCE1531FFCD", "339F94C3D1A4", "EA94C7085CB6", "B988C86D506C", "A8C558FC8495",
    "4E0A08359883", "40362CD4A2E4", "254B60AA0A9E", "EA51A6EBC9A6", "9442A40957B5", "22B148FEC23C", "9DD04C8F4885", "33079990EECE", "3B6CC3E37A63", "FFD50BD57A86",
    "95D08C6291C5", "5F246535E077", "CDF96A32746B", "1DB096540F49", "223B733916FB", "6F45C8638EA4", "85F2D2F2CADF", "64B634E1FD53", "9A2726B2836E", "40853B6714C1",
    "843F393395AC", "A640FBCAA56C", "8A0FED53D18F", "EF66FD8D51EA", "F53A1B092B9A", "EEBE0F7DE34F", "C3F7C43999DB", "E73A0C8D370A", "141944FDD5B4", "BE62747DCF5A",
    "56DCF8D7AB89", "322F96DB68C8", "02142B166432", "8F013F465B7C", "626F1F14FFA1", "EA5F9E524277", "994D4DFC36E6", "08D3FA73CE31", "5AEB0C19985C", "85EE37509ACC",
    "0DFA4F3B710C", "E31F7F18FE12", "2D2ADCB44BB9", "9BB9A3EF4F0C", "0650BE111AD9", "35FCE3B2BA9D", "772549E5E7C5", "364C7B5D306B", "8A0A22B312BB", "EE2D3711A09B",
    "795B90643F9F", "76E5F66B4036", "52E95B0D2ADB", "9EB9464ADE61", "826028C84472", "090CBE0BD4F1", "78403ACF5B40", "15A6C028F4D6", "1C8A20D67524", "A995BBFCE172",
    "E910AB339CA2", "84C4C9B60F38", "2807DCF72814", "501E46C679BB", "2EEC3E26E2F5", "3148C6C76106", "8430344CC38A", "8525B8FAA486", "2DF5B30915F0", "C663F16E59B8",
    "E1D47DDB21A2", "3A5623952FF9", "98EBCC2E6E67", "03353469BF09", "D7CADDB8329B", "5CEC1AB92855", "5F6A8BD9D284", "A3FDF47FA557", "26450253B6B6", "A0206B6183AB",
    "AC3246F072B7", "4FF3EC943193", "FF285B3E30D3", "831FD208C208", "215427E3F805", "6E6AF2C95613", "BEC98D003AE3", "CCE2816AF0EA", "7324414C02A4", "EAD90986C0B1",
    "86EC23F0F081", "373CD4005DD5", "3D22FE77764D", "B35A56F467AD", "3EB654A081DC", "F4E5F4636EED", "C057B55A0049", "FEF9C2ABAB4E", "8BFE26ECB1B2", "5658BF231250",
    "42F000CE8BAB", "0AF0D3657B4D", "42EC170DFA38", "26E111580E15", "F03CEDB53516", "C92CF1638A63", "A06D587B6720", "333481F2A350", "4290D1221EBC", "91B7F611207D",
    "C45505579E9D", "06F8BDFF7586", "633A5DDDA3DB", "AC5BBB6A38C7", "3C1611142DA3", "7A74B934DBFC", "2DAF7A6F2F66", "265EC8A99711", "912F74E985FD", "F24841608178",
    "E0263DE88774", "1D0D0DFF1A9E", "1BF02B0C5481", "634A7E68A8F9", "D9CBF04CD9D4", "F0E9EFB72E92", "7201DF6E5E84", "17DE60DD688C", "2B79A074C075", "EF44A82BE18F",
    "5AC60DE51073", "B9D3331C80C5", "AA4745299812", "4243B0CDE8B6", "42907A9A65FB", "80FD5884FAF0", "2B4A0ADE11CD", "71E4D533D6D9", "4489B0D10BB7", "BE641C440522",
    "724347E7888F", "C516295C3208", "8C0372E7AC50", "41D8BBEA0E56", "2E43C9C828D9", "2259179F5D1A", "46301C823964", "1B25C56503EB", "531F2D6D842B", "3BB30B282175",
    "7E50B940D204", "17126603DD6A", "6320CE4FC917", "5C5D3DA86953", "8D62CF986EED", "5AAB492D4A42", "B59865EED908", "656658FBB26B", "7AC3F10BAAE1", "225068CE90F4",
    "107AFDDDAD17", "8BD4E7B55229", "30BDD509D921", "FE426446CB9C", "E43AA4F39F41", "BF5CE42B4308", "C91FCF9F4B9B", "B82827B402D2", "2FCA4A0615B0", "20D925131F62",
    "7AB20019D582", "84F7B7BD199B", "2AED7650753D", "32363CFDC0FE", "EBC2FE7EA86F", "BBF19045F9FB", "1B0710C7895F", "F556DD1E3D9B", "DCE5914DF0FD", "6778B1B4C4FF",
    "061D6E93A32A", "B6179DFDA2CD", "356F33E171E9", "D62D18F69347", "B92C63B2E460", "9378A57A788B", "2EAEC7DBB67D", "9D0318DB96C1", "5E088CD57CA7", "A9B376837611",
    "2BB16298C1DA", "7521DA4B518C", "5D56DDEF4C0E", "BEE16D6063BE", "B108CE47190A", "36A3712F3752", "BADBBB207DA5", "D5255D5763E1", "D977661077D8", "E7445D1DF822",
    "BB71B89CAA32", "DF10998CBDA6", "61A823A4B632", "A56CE1D610B9", "97BDC52DB457", "999113383B05", "E1734567D139", "FCDD92052070", "49A56F8FC8FF", "7D9C7BAC58EF",
    "1A67409AE245", "F3AC4031BC16", "8DCBA9638B79", "1592D77CEFA0", "AC31C7F74080", "6F375EFA2BB4", "7FED62034324", "D1727F95C0F7", "F7E692149708", "EDE7315CE2C7",
    "18F14848EC79", "24924DFA43D7", "9F788F7235BD", "A98E758535EF", "0DE6B61843AB", "7610A3FFBB03", "595848AE76BB", "DA7BE90DB5CF", "9D164452E9E7", "6CEBFED86532"
]

# --- MA'LUMOTLARNI BOSHQARISH ---
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Faylni o'qishda xatolik: {e}")
            return {"active_subscriptions": {}, "used_keys": []}
    return {"active_subscriptions": {}, "used_keys": []}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Faylni saqlashda xatolik: {e}")

def check_user_access(user_id):
    data = load_user_data()
    user_id_str = str(user_id)
    if user_id_str in data["active_subscriptions"]:
        sub = data["active_subscriptions"][user_id_str]
        try:
            activated_at = datetime.fromisoformat(sub["activated_at"])
            expiry_date = activated_at + timedelta(days=sub["duration_days"])
            if datetime.now() < expiry_date:
                return True, expiry_date
            else:
                del data["active_subscriptions"][user_id_str]
                save_user_data(data)
                return False, None
        except Exception as e:
            logger.error(f"Sana tahlilida xatolik: {e}")
            return False, None
    return False, None

def activate_key(user_id, key_string):
    data = load_user_data()
    user_id_str = str(user_id)
    key_string = key_string.upper().strip()
    
    if key_string not in VALID_KEYS:
        return False, f"❌ Noto'g'ri kalit kiritildi! Kalit olish uchun {ADMIN_USERNAME} ga murojaat qiling."
    
    if key_string in data["used_keys"]:
        return False, f"❌ Bu kalit allaqachon ishlatilgan! Yangi kalit olish uchun {ADMIN_USERNAME} ga murojaat qiling."
    
    data["active_subscriptions"][user_id_str] = {
        "activated_at": datetime.now().isoformat(),
        "duration_days": 30,
        "key": key_string
    }
    data["used_keys"].append(key_string)
    save_user_data(data)
    expiry_date = datetime.now() + timedelta(days=30)
    return True, f"✅ Kalit faollashtirildi!\n📅 Amal qilish muddati: {expiry_date.strftime('%Y-%m-%d %H:%M')}"

# --- OCR FUNKSIYALARI ---
def clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").strip()
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def ocr_space_request(image_bytes: bytes, filename: str) -> str:
    api_key = os.getenv("OCR_SPACE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OCR_SPACE_API_KEY topilmadi. Iltimos, Environment Variables bo'limida uni sozlang.")

    boundary = "----WEAKOCRBOUNDARY7MA4YWxkTrZu0gW"
    fields = {
        "apikey": api_key, "language": DEFAULT_LANG, "isOverlayRequired": "false",
        "OCREngine": os.getenv("OCR_ENGINE", "2"), "scale": os.getenv("OCR_SCALE", "true"),
        "detectOrientation": os.getenv("OCR_DETECT_ORIENTATION", "true"),
    }

    body = io.BytesIO()
    for k, v in fields.items():
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.write(str(v).encode()); body.write(b"\r\n")

    body.write(f"--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="file"; filename="{urllib.parse.quote(filename)}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode())
    body.write(image_bytes); body.write(b"\r\n"); body.write(f"--{boundary}--\r\n".encode())

    data = body.getvalue()
    req = urllib.request.Request(OCR_API_URL, data=data, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(data)))

    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    payload = json.loads(raw)
    if payload.get("IsErroredOnProcessing"):
        msg = payload.get("ErrorMessage") or payload.get("ErrorDetails") or "OCR.Space xatosi"
        raise RuntimeError(str(msg))
    parsed = payload.get("ParsedResults") or []
    return (parsed[0].get("ParsedText") or "").strip() if parsed else ""

# --- BOT HANDLERLARI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    has_access, expiry = check_user_access(user_id)
    if has_access:
        await update.message.reply_text(f"👋 Xush kelibsiz!\n✅ Sizda faol obuna bor ({expiry.strftime('%Y-%m-%d %H:%M')}).\n📷 Rasm yuboring.")
    else:
        await update.message.reply_text(f"👋 Salom! Botdan foydalanish uchun kalitni kiriting.\n🔑 Kalitni shunchaki yozib yuboring.\nAgar kalitingiz bo'lmasa, {ADMIN_USERNAME} ga murojaat qiling.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    if not text: return

    has_access, _ = check_user_access(user_id)
    if not has_access:
        success, msg = activate_key(user_id, text)
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("📷 Rasm yuboring, men undagi matnni o'qib beraman.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    has_access, _ = check_user_access(user_id)
    
    if not has_access:
        await update.message.reply_text(f"❌ Sizda faol obuna yo'q! Kalitni kiriting yoki {ADMIN_USERNAME} ga murojaat qiling.")
        return

    try:
        photo_file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await photo_file.download_to_memory(buf)
        image_bytes = buf.getvalue()

        await update.message.reply_chat_action(ChatAction.TYPING)
        
        text = ocr_space_request(image_bytes, "image.jpg")
        if not text:
            await update.message.reply_text("❌ Rasmda matn topilmadi.")
        else:
            cleaned = clean_text(text)
            # HTML escape qilish (xatolik bermasligi uchun)
            escaped_text = html_escape(cleaned)
            # Nusxa olish oson bo'lishi uchun <code> tegiga o'rash
            formatted_text = f"<code>{escaped_text}</code>"
            
            if len(formatted_text) > 4000:
                # Agar matn juda uzun bo'lsa, bo'laklab yuborish
                for i in range(0, len(cleaned), 3500):
                    chunk = html_escape(cleaned[i:i+3500])
                    await update.message.reply_text(f"<code>{chunk}</code>", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(formatted_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"OCR xatoligi: {e}")
        await update.message.reply_text(f"❌ Xatolik yuz berdi: {str(e)}")

async def main_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi! Bot ishga tushmadi.")
        return

    try:
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        await application.initialize()
        await application.start()
        logger.info("Bot polling rejimida ishga tushdi.")
        await application.updater.start_polling()
        
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")

if __name__ == "__main__":
    # Flaskni alohida threadda ishga tushirish
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Botni asosiy threadda ishga tushirish
    try:
        asyncio.run(main_bot())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
    except Exception as e:
        logger.error(f"Asosiy loopda xatolik: {e}")
