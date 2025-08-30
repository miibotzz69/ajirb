import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TOKEN = "ISI_TOKEN_BOT_LU"
OWNER_ID = 123456789  # ganti pake user id lu
PREM_FILE = "prem.txt"

# ---------- Helper ----------
def load_prem():
    if not os.path.exists(PREM_FILE):
        return {}
    data = {}
    with open(PREM_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                user, pw, exp = line.split(":")
                data[user] = {"pw": pw, "exp": int(exp)}
            except:
                pass
    return data

def save_prem(data):
    with open(PREM_FILE, "w") as f:
        for user, info in data.items():
            f.write(f"{user}:{info['pw']}:{info['exp']}\n")

def is_valid(user, pw):
    data = load_prem()
    if user in data:
        if data[user]["pw"] == pw and (data[user]["exp"] == 0 or data[user]["exp"] > int(time.time())):
            return True
    return False

# ---------- Handler ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Masukin user:pw dulu untuk login.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text or ":" not in update.message.text:
        return
    user, pw = update.message.text.split(":", 1)
    if is_valid(user, pw):
        kb = [
            [InlineKeyboardButton("DELAY HARD", callback_data="vor_delay")],
            [InlineKeyboardButton("FORCLOSE ALL WA", callback_data="vor_fc")],
            [InlineKeyboardButton("CRASH IPHONE", callback_data="vor_crash")]
        ]
        await update.message.reply_text(
            "WELCOME TO BOT BUG SIMPEL\n--------VORTEXSHADE--------",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        context.user_data["login"] = True
    else:
        await update.message.reply_text("Login gagal, user/pw salah atau expired.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("login"):
        await query.edit_message_text("Login dulu bro.")
        return
    context.user_data["mode"] = query.data
    await query.message.reply_text("SILAHKAN KIRIM NOMER TARGET\nAWALI DENGAN 62xxx SELAMAT BUG")

async def nomor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("login"):
        return
    nomor = update.message.text.strip()
    if nomor.startswith("62") and context.user_data.get("mode"):
        perintah = f"/{context.user_data['mode']} {nomor}"
        await context.bot.send_message(OWNER_ID, perintah)
        await update.message.reply_text("Target berhasil dikirim ke owner 🚀")

# ---------- Owner command ----------
async def addprem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return
    if len(context.args) < 1:
        await update.message.reply_text("Format: /add user:pw [hari]")
        return
    up = context.args[0]
    if ":" not in up:
        await update.message.reply_text("Format salah.")
        return
    user, pw = up.split(":", 1)
    hari = int(context.args[1]) if len(context.args) > 1 else 0
    exp = int(time.time()) + hari*86400 if hari > 0 else 0
    data = load_prem()
    data[user] = {"pw": pw, "exp": exp}
    save_prem(data)
    await update.message.reply_text(f"User {user} ditambahin premium ({'no limit' if exp==0 else str(hari)+' hari'})")

async def listprem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return
    data = load_prem()
    teks = "Daftar premium:\n"
    for u, info in data.items():
        if info["exp"] == 0:
            teks += f"- {u} :pw={info['pw']} (no limit)\n"
        else:
            sisa = info["exp"] - int(time.time())
            teks += f"- {u} :pw={info['pw']} (sisa {sisa//86400} hari)\n"
    await update.message.reply_text(teks)

# ---------- Main ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, login))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nomor))
    app.add_handler(CommandHandler("add", addprem))
    app.add_handler(CommandHandler("prem", listprem))
    app.run_polling()

if __name__ == "__main__":
    main()
