import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from config import TOKEN, ADMIN_ID
import database as db

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# MENU
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("🎮 O'yinlar")
menu.add("💰 Balans", "👥 Referal")
menu.add("🎁 Promokod")


games = ReplyKeyboardMarkup(resize_keyboard=True)
games.add("Narvon", "Sapyor")
games.add("Crash", "Gildirak")
games.add("Minora")
games.add("⬅️ Orqaga")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    args = message.get_args()
    user_id = message.from_user.id

    if args and int(args) != user_id:
        db.add_user(user_id, int(args))
        db.update_balance(int(args), 3)
        db.add_referral(int(args))
    else:
        db.add_user(user_id)

    await message.answer("🎉 Xush kelibsiz!", reply_markup=menu)


@dp.message_handler(lambda message: message.text == "🎮 O'yinlar")
async def games_menu(message: types.Message):
    await message.answer("O'yinni tanlang:", reply_markup=games)


@dp.message_handler(lambda message: message.text == "⬅️ Orqaga")
async def back(message: types.Message):
    await message.answer("Asosiy menyu", reply_markup=menu)


@dp.message_handler(lambda message: message.text == "💰 Balans")
async def balance(message: types.Message):
    bal = db.get_balance(message.from_user.id)
    await message.answer(f"💰 Balans: {bal} coin")


@dp.message_handler(lambda message: message.text == "👥 Referal")
async def ref(message: types.Message):
    link = f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}"
    await message.answer(f"👥 Referal linkingiz:\n{link}\n\nHar odam uchun 3 coin")


@dp.message_handler(lambda message: message.text in ["Narvon","Sapyor","Crash","Gildirak","Minora"])
async def game_advice(message: types.Message):
    user_id = message.from_user.id
    bal = db.get_balance(user_id)

    if bal < 1:
        await message.answer("❌ Coin yetarli emas")
        return

    db.update_balance(user_id, -1)

    if message.text == "Narvon":
        advice = f"{random.randint(1,7)} pog'onagacha boring"
    elif message.text == "Sapyor":
        advice = f"Xavfsiz katak: {random.randint(1,25)}"
    elif message.text == "Crash":
        advice = f"x{round(random.uniform(1.5,3.5),2)} da chiqing"
    elif message.text == "Gildirak":
        advice = random.choice(["Qizil","Yashil","Ko‘k"])
    elif message.text == "Minora":
        advice = f"{random.randint(1,10)} qavatgacha boring"

    await message.answer(f"💡 Maslahat:\n{advice}")


@dp.message_handler(commands=['addcoin'])
async def addcoin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        user_id, amount = map(int, message.get_args().split())
        db.update_balance(user_id, amount)
        await message.answer("✅ Coin qo‘shildi")


@dp.message_handler(commands=['createpromo'])
async def createpromo(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        code, reward = message.get_args().split()
        db.cursor.execute("INSERT INTO promocodes VALUES (?,?)", (code, reward))
        db.conn.commit()
        await message.answer("🎁 Promokod yaratildi")


@dp.message_handler(lambda message: message.text == "🎁 Promokod")
async def promo_info(message: types.Message):
    await message.answer("Promo kodni kiriting: /promo KOD")


@dp.message_handler(commands=['promo'])
async def usepromo(message: types.Message):
    code = message.get_args()
    db.cursor.execute("SELECT reward FROM promocodes WHERE code=?", (code,))
    data = db.cursor.fetchone()

    if data:
        db.update_balance(message.from_user.id, int(data[0]))
        db.cursor.execute("DELETE FROM promocodes WHERE code=?", (code,))
        db.conn.commit()
        await message.answer("🎁 Coin qo‘shildi")
    else:
        await message.answer("❌ Noto‘g‘ri kod")


if __name__ == "__main__":
    executor.start_polling(dp)
