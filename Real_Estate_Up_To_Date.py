import os
import re
import telebot
import pandas as pd
from datetime import datetime

# Render Environment Variable မှ Telegram Token ကို ယူခြင်း
TELETOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELETOKEN)

EXCEL_FILE = "real_estate_data.xlsx"

def parse_real_estate_post(post_text):
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
        
        # ဖုန်းနံပါတ် ရှာရန်
        phone_match = re.search(r'(09[-0-9]{7,})', line)
        if phone_match:
            phone_str = phone_match.group(1)
        else:
            notes.append(line)
            
    # အချက်အလက်များကို List ပုံစံ ပြန်ထုတ်ပေးခြင်း
    row_data = [
        str(datetime.now()),
        township,
        ward,
        dimensions,
        ownership,
        price,
        phone_str,
        " | ".join(notes)
    ]
    return row_data

def save_to_excel(row_data):
    columns = ["Date & Time", "Township", "Ward", "Dimensions", "Ownership", "Price", "Phone", "Notes"]
    
    # Excel ဖိုင် ရှိမရှိ စစ်ဆေးပြီး အသစ်ဖန်တီးခြင်း သို့မဟုတ် ပေါင်းထည့်ခြင်း
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        df_new = pd.DataFrame([row_data], columns=columns)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = pd.DataFrame([row_data], columns=columns)
        
    df.to_excel(EXCEL_FILE, index=False)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    post_text = message.text
    
    # Real Estate Data ကို Parse လုပ်ပြီး Excel ထဲ သိမ်းမည်
    row_data = parse_real_estate_post(post_text)
    save_to_excel(row_data)
    
    bot.reply_to(message, "အချက်အလက်များကို Excel ဖိုင်ထဲသို့ အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")

if __name__ == "__main__":
    bot.infinity_polling()
