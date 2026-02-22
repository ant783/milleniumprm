import asyncio
import random
import aiohttp
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

# Замените на ваш токен
BOT_TOKEN = '8275812174:AAHGIrL3Uw8AN7TKdNAtUZYFTi0lQu1Ni-A'
PROXY_URL = 'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище лимитов: {user_id: last_update_time}
user_limits = {}

async def fetch_proxies():
    async with aiohttp.ClientSession() as session:
        async with session.get(PROXY_URL) as resp:
            if resp.status == 200:
                content = await resp.text()
                proxies = [line.strip() for line in content.splitlines() if line.strip()]
                return proxies
    return []

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить прокси", callback_data="update_proxies")]
    ])
    await message.answer(
        "👋 Добро пожаловать! Нажмите кнопку ниже, чтобы получить 3 случайных бесплатных MTProto-прокси для Telegram.\n\n"
        "Доступно 1 раз в сутки на пользователя.",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "update_proxies")
async def update_proxies(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    now = datetime.now()
    
    last_update = user_limits.get(user_id)
    if last_update and now - last_update < timedelta(days=1):
        time_left = timedelta(days=1) - (now - last_update)
        hours = int(time_left.total_seconds() // 3600)
        mins = int((time_left.total_seconds() % 3600) // 60)
        await callback.answer(f"⏳ Подождите {hours}ч {mins}м до следующего обновления!")
        return
    
    proxies = await fetch_proxies()
    if not proxies:
        await callback.message.edit_text("❌ Не удалось загрузить прокси. Попробуйте позже.")
        return
    
    selected = random.sample(proxies, 3)
    text = "🔗 **Вот 3 случайных бесплатных MTProto-прокси:**\n\n"
    for i, proxy in enumerate(selected, 1):
        text += f"{i}. `{proxy}`\n"
    text += "\nНажмите на ссылки, чтобы подключить в Telegram!"
    
    user_limits[user_id] = now
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer("✅ Прокси обновлены!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
