import os
import re
import telebot
import pandas as pd
from datetime import datetime

# ထည့်သွင်းပေးထားသော Telegram Bot Token
TELETOKEN = '8923937624:AAGitSxbFpt7Ztww82s0lqryBq167z06cO0'
bot = telebot.TeleBot(TELETOKEN)

EXCEL_FILE = "real_estate_data.xlsx"

def parse_real_estate_post(post_text):
    link_match = re.search(r'(https?://(?:www\.)?(?:facebook\.com|fb\.watch|t\.me)/\S+)', post_text)
    extracted_link = link_match.group(1) if link_match else ""

    lines = [line.strip() for line in post_text.split('\n') if line.strip()]
    
    township, ward, dimensions, ownership, price, phone_str = "", "", "", "", "", ""
    notes = []
    
    for line in lines:
        if 'ဒဂုံ' in line:
            if 'တောင်ဒဂုံ' in line:
                township = "South Dagon"
            elif 'ဒဂုံဆိပ်ကမ်း' in line:
                township = "Dagon Seikkan"
            elif 'မြောက်ဒဂုံ' in line:
                township = "North Dagon"
            else:
                township = "Dagon"
        elif 'အင်းစိန်' in line:
            township = "Insein"
        elif 'လှိုင်' in line:
            township = "Hlaing"
        
        phone_match = re.search(r'(09[-0-9]{7,})', line)
        if phone_match:
            phone_str = phone_match.group(1)
        else:
            notes.append(line)
            
    row_data = [
        str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        township,
        phone_str,
        extracted_link,
        " | ".join(notes)
    ]
    return row_data

def save_to_excel(row_data):
    columns = ["Date & Time", "Township", "Phone", "Link", "Notes"]
    
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        df_new = pd.DataFrame([row_data], columns=columns)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = pd.DataFrame([row_data], columns=columns)
        
    df.to_excel(EXCEL_FILE, index=False)

def undo_last_row():
    if not os.path.exists(EXCEL_FILE):
        return "Excel ဖိုင် မရှိသေးပါ။"
    
    df = pd.read_excel(EXCEL_FILE)
    if len(df) == 0:
        return "ဖျက်စရာ အချက်အလက် မရှိတော့ပါ။"
    
    df = df.iloc[:-1]
    df.to_excel(EXCEL_FILE, index=False)
    return "🗑️ နောက်ဆုံးထည့်သွင်းခဲ့သော အချက်အလက်ကို အောင်မြင်စွာ ပြန်ဖျက်လိုက်ပါပြီ။"

# /undo အမိန့်
@bot.message_handler(commands=['undo'])
def handle_undo(message):
    result_message = undo_last_row()
    bot.reply_to(message, result_message)

# 📊 Excel ဖိုင်ကို Telegram ထဲ တိုက်ရိုက် တောင်းရန် /getexcel အမိန့်
@bot.message_handler(commands=['getexcel'])
def handle_get_excel(message):
    if os.path.exists(EXCEL_FILE) and os.path.getsize(EXCEL_FILE) > 0:
        with open(EXCEL_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="📂 လက်ရှိ Excel ဒေတာဖိုင်")
    else:
        bot.reply_to(message, "⚠️ Excel ဖိုင် မရှိသေးပါ (သို့မဟုတ်) ဒေတာ မဝင်သေးပါ။")

# Telegram Channel ထဲမှ ပို့စ်များကို ဖမ်းယူရန်
@bot.channel_post_handler(func=lambda message: True)
def handle_channel_posts(message):
    if message.text:
        row_data = parse_real_estate_post(message.text)
        save_to_excel(row_data)

# ပုံမှန် Chat ထဲမှ ပို့သော စာများကို လက်ခံရန်
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    post_text = message.text
    row_data = parse_real_estate_post(post_text)
    save_to_excel(row_data)
    bot.reply_to(message, "✅ အချက်အလက်များကို Excel ဖိုင်ထဲသို့ အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")

if __name__ == "__main__":
    bot.infinity_polling()
