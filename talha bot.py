import telebot
import requests

BOT_TOKEN = "8796267960:AAHx3gDbetQl2Jyp6Od4GOc8vs6IwD8o5vY"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, 
"""
🎬 *Netflix Cookie Checker Bot*

Commands:
/cookie NetflixId=value - Check cookie working hai ya nahi
/help - Ye message

*Example:*
/cookie NetflixId=abcd1234...

*Note:* Kuch cookies mein SecureNetflixId bhi hota hai, dono ek saath daal.
""", parse_mode="Markdown")

@bot.message_handler(commands=['cookie'])
def check_cookie(message):
    status_msg = None
    try:
        cookie_str = message.text.replace('/cookie', '').strip()
        
        if not cookie_str:
            bot.reply_to(message, "❌ Cookie to daal bhai!\nExample: /cookie NetflixId=ct%3D...")
            return
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "keep-alive",
            "Referer": "https://www.netflix.com/Login"
        }
        
        if not cookie_str.startswith("NetflixId=") and not cookie_str.startswith("SecureNetflixId="):
            cookie_str = f"NetflixId={cookie_str}"
        
        headers["Cookie"] = cookie_str
        
        status_msg = bot.reply_to(message, "⏳ Checking...")
        
        session = requests.Session()
        session.headers.update(headers)
        r = session.get("https://www.netflix.com/browse", allow_redirects=False, timeout=15)
        
        response_text = r.text.lower()
        
        if r.status_code == 200:
            if "profile" in response_text or "browse" in response_text or "profiles" in response_text:
                bot.edit_message_text("✅ *WORKING* 🎉\n\nAccount valid hai!", 
                                    chat_id=message.chat.id, message_id=status_msg.message_id,
                                    parse_mode="Markdown")
            elif "login" in response_text:
                bot.edit_message_text("❌ *INVALID* 😞\n\nCookie expired ya galat hai.", 
                                    chat_id=message.chat.id, message_id=status_msg.message_id,
                                    parse_mode="Markdown")
            else:
                bot.edit_message_text("⚠️ *UNKNOWN*\nStatus 200 par unknown response.", 
                                    chat_id=message.chat.id, message_id=status_msg.message_id,
                                    parse_mode="Markdown")
        elif r.status_code == 302:
            location = r.headers.get('Location', '')
            if 'login' in location:
                bot.edit_message_text("❌ *EXPIRED* 🔴\n\nSession expired.", 
                                    chat_id=message.chat.id, message_id=status_msg.message_id,
                                    parse_mode="Markdown")
            else:
                bot.edit_message_text(f"⚠️ Redirect: {location}", 
                                    chat_id=message.chat.id, message_id=status_msg.message_id)
        elif r.status_code == 403:
            bot.edit_message_text("⛔ *BLOCKED*\n\nNetflix ne block kiya. VPN change kar.", 
                                chat_id=message.chat.id, message_id=status_msg.message_id,
                                parse_mode="Markdown")
        else:
            bot.edit_message_text(f"⚠️ Status: {r.status_code}", 
                                chat_id=message.chat.id, message_id=status_msg.message_id)
                                
    except requests.exceptions.Timeout:
        msg = status_msg if status_msg else message
        bot.edit_message_text("⏰ *TIMEOUT*", chat_id=message.chat.id, 
                            message_id=msg.message_id, parse_mode="Markdown")
    except Exception as e:
        msg = status_msg if status_msg else message
        bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id,
                            message_id=msg.message_id)

@bot.message_handler(func=lambda msg: True)
def handle_all(message):
    text = message.text.strip()
    if text.startswith("NetflixId=") or text.startswith("SecureNetflixId="):
        check_cookie(message)
    else:
        bot.reply_to(message, "❌ /cookie <tumhari_cookie> use kar.")

print("🤖 Bot chal raha hai...")
if __name__ == "__main__":
    bot.polling(none_stop=True)