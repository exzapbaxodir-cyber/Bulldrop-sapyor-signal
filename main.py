import logging
import random
import sqlite3
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "8692829092:AAEzIExDusdb7PpDOy04bTspAFQnsS5v2l8"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Database
conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    ref_by INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS promocodes (
    code TEXT PRIMARY KEY,
    reward INTEGER
)
""")

conn.commit()


# Start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    args = message.get_args()
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        ref_by = None
        if args:
            ref_by = int(args)
            if ref_by != user_id:
                cursor.execute("UPDATE users SET balance = balance + 3 WHERE user_id=?", (ref_by,))
        cursor.execute("INSERT INTO users (user_id, balance, ref_by) VALUES (?, 5, ?)", (user_id, ref_by))
        conn.commit()

    ref_link = f"https://t.me/{(await bot.get_me()).username}?start={user_id}"
    await message.answer(f"""
🎉 Xush kelibsiz!

💰 Boshlang‘ich balans: 5 coin
👥 Referal link:
{ref_link}

Maslahat olish uchun o‘yin nomini yozing:
Narvon / Sapyor / Crash / Gildirak / Minora
""")


# Balans
@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (message.from_user.id,))
    bal = cursor.fetchone()[0]
    await message.answer(f"💰 Sizning balansingiz: {bal} coin")


# O'yin maslahat
@dp.message_handler(lambda message: message.text.lower() in ['narvon','sapyor','crash','gildirak','minora'])
async def game_advice(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cursor.fetchone()[0]

    if bal < 1:
        await message.answer("❌ Coin yetarli emas")
        return

    cursor.execute("UPDATE users SET balance = balance - 1 WHERE user_id=?", (user_id,))
    conn.commit()

    game = message.text.lower()

    if game == "narvon":
        advice = f"📊 Qadam: {random.randint(1,7)} pog'onagacha boring"
    elif game == "sapyor":
        advice = f"🟩 Xavfsiz katak: {random.randint(1,25)}"
    elif game == "crash":
        advice = f"🚀 Chiqish koeff: x{round(random.uniform(1.5,3.5),2)}"
    elif game == "gildirak":
        advice = f"🎡 Rang: {random.choice(['Qizil','Yashil','Ko‘k'])}"
    elif game == "minora":
        advice = f"🏰 Qavat: {random.randint(1,10)}"

    await message.answer(f"💡 Maslahat:\n{advice}")


# Promokod
@dp.message_handler(commands=['promo'])
async def promo(message: types.Message):
    code = message.get_args()

    cursor.execute("SELECT reward FROM promocodes WHERE code=?", (code,))
    promo = cursor.fetchone()

    if promo:
        reward = promo[0]
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (reward, message.from_user.id))
        cursor.execute("DELETE FROM promocodes WHERE code=?", (code,))
        conn.commit()
        await message.answer(f"🎁 Siz {reward} coin oldingiz!")
    else:
        await message.answer("❌ Promokod noto‘g‘ri")


# Admin balans qo'shish
@dp.message_handler(commands=['addcoin'])
async def addcoin(message: types.Message):
    ADMIN_ID = 123456789  # admin id

    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id, amount = map(int, message.get_args().split())
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
        conn.commit()
        await message.answer("✅ Coin qo‘shildi")
    except:
        await message.answer("Format: /addcoin user_id amount")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
