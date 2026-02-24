import asyncio
import random
import re
import aiohttp
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ BOT_TOKEN ХРАНИТСЯ ПРЯМО В ЭТОМ ФАЙЛЕ
BOT_TOKEN = "8275812174:AAEY3EDh3KTvA1XrgCAnD19QaJcPxWMWQTU"  # ← ЗАМЕНИТЕ НА СВОЙ

# ✅ ID АДМИНА-СОЗДАТЕЛЯ (ваш Telegram ID)
ADMIN_ID = 1591887659  # ← ЗАМЕНИТЕ НА СВОЙ TELEGRAM ID

PROXY_URL_GITHUB = 'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt'
PROXY_URL_ARGH94 = 'https://raw.githubusercontent.com/Argh94/Proxy-List/refs/heads/main/MTProto.txt'
PROXY_URL_MTPRO = 'https://mtpro.xyz/'
PROXY_URL_MTPRO_RU = 'https://mtpro.xyz/mtproto-ru'
ADMIN_BOT_URL = 'https://raw.githubusercontent.com/ant783/milleniumprm/blob/main/milleniumprm_bot.py'

# Проверка токена
if not BOT_TOKEN or BOT_TOKEN == "7769789234:AAFGawI5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k":
    print("❌ ОШИБКА: Замените BOT_TOKEN на ваш реальный токен!")
    exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def fetch_proxies_github():
    """GitHub SoliSpirit"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_GITHUB, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    proxies = [line.strip() for line in content.splitlines() if line.strip()]
                    logger.info(f"✅ GitHub SoliSpirit: {len(proxies)} прокси")
                    return proxies
    except Exception as e:
        logger.error(f"❌ GitHub SoliSpirit: {e}")
    return []

async def fetch_proxies_argh94():
    """Argh94"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_ARGH94, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    proxies = [line.strip() for line in content.splitlines() if line.strip()]
                    logger.info(f"✅ Argh94: {len(proxies)} прокси")
                    return proxies
    except Exception as e:
        logger.error(f"❌ Argh94: {e}")
    return []

async def fetch_proxies_mtpro():
    """mtpro.xyz"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_MTPRO, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    proxy_links = re.findall(r'(?:https://t\.me/proxy\?[^"\s]+|tg://proxy\?[^"\s]+)', html)
                    clean_proxies = [link.strip('"\'').rstrip() for link in proxy_links 
                                   if link.strip('"\'').rstrip().startswith(('https://t.me/proxy?', 'tg://proxy?'))]
                    logger.info(f"✅ mtpro.xyz: {len(clean_proxies)} прокси")
                    return clean_proxies
    except Exception as e:
        logger.error(f"❌ mtpro.xyz: {e}")
    return []

async def fetch_proxies_mtpro_ru():
    """mtproto-ru"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_MTPRO_RU, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    proxy_links = re.findall(r'(?:https://t\.me/proxy\?[^"\s]+|tg://proxy\?[^"\s]+)', html)
                    clean_proxies = [link.strip('"\'').rstrip() for link in proxy_links 
                                   if link.strip('"\'').rstrip().startswith(('https://t.me/proxy?', 'tg://proxy?'))]
                    logger.info(f"✅ mtproto-ru: {len(clean_proxies)} прокси")
                    return clean_proxies
    except Exception as e:
        logger.error(f"❌ mtproto-ru: {e}")
    return []

async def fetch_admin_bot():
    """Загружает код админ-бота"""
    try:
        raw_url = 'https://raw.githubusercontent.com/ant783/milleniumprm/main/milleniumprm_bot.py'
        async with aiohttp.ClientSession() as session:
            async with session.get(raw_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    code = await resp.text()
                    logger.info("✅ Админ-бот обновлен")
                    return code[:500] + "..." if len(code) > 500 else code
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки админ-бота: {e}")
    return "❌ Не удалось загрузить"

async def fetch_all_proxies():
    """Fallback логика 4 источников"""
    all_proxies = []
    
    github_proxies = await fetch_proxies_github()
    if github_proxies: return list(set(github_proxies))
    
    argh94_proxies = await fetch_proxies_argh94()
    if argh94_proxies: return list(set(argh94_proxies))
    
    mtpro_proxies = await fetch_proxies_mtpro()
    if mtpro_proxies: return list(set(mtpro_proxies))
    
    mtpro_ru_proxies = await fetch_proxies_mtpro_ru()
    if mtpro_ru_proxies: return list(set(mtpro_ru_proxies))
    
    return []

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Главное меню"""
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить прокси", callback_data="update_proxies")]
    ])
    
    # ✅ КНОПКА АДМИНА только для создателя
    if user_id == ADMIN_ID:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔧 Админ: Обновить данные", callback_data="admin_update")])
    
    welcome_text = (
        "👋 **Добро пожаловать!**\n\n"
        "🔥 **3 случайных MTProto прокси**\n\n"
        "⚡ **Нажмите кнопку ниже и получишь результат!**"
    )
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "update_proxies")
async def update_proxies(callback: types.CallbackQuery):
    """Показывает прокси"""
    await callback.message.edit_text("⏳ Загружаем свежие прокси...")
    
    proxies = await fetch_all_proxies()
    if not proxies:
        await callback.message.edit_text("❌ Прокси временно недоступны.")
        return
    
    available_count = min(len(proxies), 3)
    selected = random.sample(proxies, available_count)
    
    keyboard_rows = [[InlineKeyboardButton(text="connect", url=proxy)] for proxy in selected]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    count_text = f"{available_count} случайных MTProto прокси"
    text = f"🔥 **{count_text}:**\n\n"
    for i, proxy in enumerate(selected, 1):
        short_link = proxy[:60] + "..." if len(proxy) > 60 else proxy
        text += f"{i}. `{short_link}`\n\n"
    text += "👇 **Кнопка connect после каждого прокси!**"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer("✅ Готово!")

@dp.callback_query(lambda c: c.data == "admin_update")
async def admin_update(callback: types.CallbackQuery):
    """🔧 АДМИН: Обновить данные"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ только для админа!")
        return
    
    await callback.message.edit_text("🔧 Обновляем данные...")
    
    # Обновляем прокси
    proxies = await fetch_all_proxies()
    proxy_count = len(proxies) if proxies else 0
    
    # Обновляем админ-бот
    admin_code = await fetch_admin_bot()
    
    admin_text = (
        f"🔧 **Обновление завершено!**\n\n"
        f"📊 **Прокси:** {proxy_count} шт.\n"
        f"📜 **Админ-бот:** {'✅ Загружен' if '❌' not in admin_code else '❌ Ошибка'}\n\n"
        f"💻 **Последние строки кода админ-бота:**\n"
        f"```{admin_code}```"
    )
    
    await callback.message.edit_text(admin_text, parse_mode="Markdown")
    await callback.answer("✅ Обновлено!")

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    help_text = (
        "ℹ️ **Инфо:**\n\n"
        "🔗 **Кнопки connect** = tg://proxy\n\n"
        f"🔧 **Админ:** @{message.bot.username}\n"
        "🔧 **/start** - Меню"
    )
    await message.answer(help_text, parse_mode="Markdown")

async def main():
    logger.info("🚀 Бот запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
