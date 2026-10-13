import os
import re
import requests
from telebot import TeleBot

# Render ရဲ့ Environment Variables ထဲမှ Token များကို ဆွဲယူခြင်း (လုံခြုံရေးအတွက်)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_WEBAPP_URL = os.environ.get('GOOGLE_WEBAPP_URL')

bot = TeleBot(TELEGRAM_TOKEN)

def parse_real_estate_post(post_text):
    lines = [line.strip() for line in post_text.split('\n') if line.strip()]
    
    township, ward, dimensions, ownership, price, phone_str = "", "", "", "", "", ""
    notes = []
    
    if "တောင်ဒဂုံ" in post_text:
        township = "South Dagon"
    elif "ဒဂုံဆိပ်ကမ်း" in post_text:
        township = "Dagon Seikkan"
        
    ward_match = re.search(r'([0-9０-၉]+)\s*ရပ်ကွက်', post_text)
    if ward_match:
        ward = ward_match.group(1).translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))
        
    dim_match = re.search(r"([0-9'\s×x✕\-ပေ]+(?:ပေ)?)", post_text)
    if dim_match:
        dimensions = dim_match.group(0).strip()
        
    phones = re.findall(r'09\s*[0-9\s]{7,12}', post_text)
    phone_str = " ".join(["".join(p.split()) for p in phones])
    
    row_data = [
        lines[0] if lines else "", township, ward, "အရောင်း", dimensions,
        "အိမ်ပါ" if "အိမ်ပါ" in post_text else "မြေကွက်", "", "",
        "၊ ".join(notes), ownership, phone_str, "ရ", price, "", "Facebook", ""
    ]
    return row_data

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    post_text = message.text
    
    # Data ခွဲထုတ်ခြင်း
    row_data = parse_real_estate_post(post_text)
    
    # Google Sheet (Apps Script WebApp) သို့ ပို့ခြင်း
    try:
        response = requests.post(GOOGLE_WEBAPP_URL, json={"row_data": row_data})
        if response.status_code == 200:
            bot.reply_to(message, "✅ Google Sheet ထဲသို့ Auto သွင်းပြီးပါပြီ!")
        else:
            bot.reply_to(message, "❌ မအောင်မြင်ပါ။ ပြန်လည် ကြိုးစားပါ။")
    except Exception as e:
        bot.reply_to(message, f"❌ Error တက်နေပါသည်: {str(e)}")

bot.infinity_polling()
