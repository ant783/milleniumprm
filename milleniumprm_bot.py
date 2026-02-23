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

PROXY_URL_GITHUB = 'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt'
PROXY_URL_ARGH94 = 'https://raw.githubusercontent.com/Argh94/Proxy-List/refs/heads/main/MTProto.txt'
PROXY_URL_MTPRO = 'https://mtpro.xyz/'
PROXY_URL_MTPRO_RU = 'https://mtpro.xyz/mtproto-ru'

# Проверка токена
if not BOT_TOKEN or BOT_TOKEN == "7769789234:AAFGawI5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k":
    print("❌ ОШИБКА: Замените BOT_TOKEN на ваш реальный токен!")
    exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def fetch_proxies_github():
    """Загружает прокси с GitHub SoliSpirit"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_GITHUB, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    proxies = [line.strip() for line in content.splitlines() if line.strip()]
                    logger.info(f"✅ GitHub SoliSpirit: Загружено {len(proxies)} прокси")
                    return proxies
    except Exception as e:
        logger.error(f"❌ GitHub SoliSpirit недоступен: {e}")
    return []

async def fetch_proxies_argh94():
    """Загружает прокси с Argh94"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_ARGH94, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    proxies = [line.strip() for line in content.splitlines() if line.strip()]
                    logger.info(f"✅ Argh94: Загружено {len(proxies)} прокси")
                    return proxies
    except Exception as e:
        logger.error(f"❌ Argh94 недоступен: {e}")
    return []

async def fetch_proxies_mtpro():
    """Парсит прокси с mtpro.xyz"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_MTPRO, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    proxy_links = re.findall(r'(?:https://t\.me/proxy\?[^"\s]+|tg://proxy\?[^"\s]+)', html)
                    clean_proxies = [link.strip('"\'').rstrip() for link in proxy_links 
                                   if link.strip('"\'').rstrip().startswith(('https://t.me/proxy?', 'tg://proxy?'))]
                    logger.info(f"✅ mtpro.xyz: Найдено {len(clean_proxies)} прокси")
                    return clean_proxies
    except Exception as e:
        logger.error(f"❌ mtpro.xyz недоступен: {e}")
    return []

async def fetch_proxies_mtpro_ru():
    """Парсит прокси с mtproto-ru"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_MTPRO_RU, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    proxy_links = re.findall(r'(?:https://t\.me/proxy\?[^"\s]+|tg://proxy\?[^"\s]+)', html)
                    clean_proxies = [link.strip('"\'').rstrip() for link in proxy_links 
                                   if link.strip('"\'').rstrip().startswith(('https://t.me/proxy?', 'tg://proxy?'))]
                    logger.info(f"✅ mtproto-ru: Найдено {len(clean_proxies)} прокси")
                    return clean_proxies
    except Exception as e:
        logger.error(f"❌ mtproto-ru недоступен: {e}")
    return []

async def fetch_all_proxies():
    """Загружает прокси с fallback логикой (4 источника)"""
    all_proxies = []
    
    # 1. Пробуем GitHub SoliSpirit
    github_proxies = await fetch_proxies_github()
    if github_proxies:
        all_proxies.extend(github_proxies)
        logger.info("✅ Используем GitHub SoliSpirit")
        return list(set(all_proxies))
    
    # 2. Argh94
    logger.info("🔄 SoliSpirit недоступен, пробуем Argh94...")
    argh94_proxies = await fetch_proxies_argh94()
    if argh94_proxies:
        all_proxies.extend(argh94_proxies)
        logger.info("✅ Используем Argh94 прокси")
        return list(set(all_proxies))
    
    # 3. mtpro.xyz
    logger.info("🔄 Argh94 недоступен, пробуем mtpro.xyz...")
    mtpro_proxies = await fetch_proxies_mtpro()
    if mtpro_proxies:
        all_proxies.extend(mtpro_proxies)
        logger.info("✅ Используем mtpro.xyz прокси")
        return list(set(all_proxies))
    
    # 4. mtproto-ru
    logger.info("🔄 mtpro.xyz недоступен, пробуем mtproto-ru...")
    mtpro_ru_proxies = await fetch_proxies_mtpro_ru()
    if mtpro_ru_proxies:
        all_proxies.extend(mtpro_ru_proxies)
        logger.info("✅ Используем mtproto-ru прокси")
        return list(set(all_proxies))
    
    logger.error("❌ Все источники недоступны!")
    return []

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить прокси", callback_data="update_proxies")]
    ])
    welcome_text = (
        "👋 **Добро пожаловать!**\n\n"
        "🔥 **3 случайных MTProto прокси**\n\n"
        "⚡ **Нажмите кнопку ниже и получишь результат!**"
    )
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "update_proxies")
async def update_proxies(callback: types.CallbackQuery):
    """Обработчик кнопки - показывает 1, 2 или 3 прокси"""
    await callback.message.edit_text("⏳ Загружаем свежие прокси...")
    
    proxies = await fetch_all_proxies()
    if not proxies:
        await callback.message.edit_text("❌ Прокси временно недоступны. Попробуйте позже.")
        return
    
    # ✅ ПОКАЗЫВАЕМ ВСЕ ДОСТУПНЫЕ ПРОКСИ (1, 2 или 3)
    available_count = min(len(proxies), 3)
    selected = random.sample(proxies, available_count)
    
    # Создаем клавиатуру ДИНАМИЧЕСКИ под количество прокси
    keyboard_rows = []
    for proxy in selected:
        keyboard_rows.append([InlineKeyboardButton(text="connect", url=proxy)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    # Динамический текст
    count_text = f"{available_count} случайных MTProto прокси"
    text = f"🔥 **{count_text}:**\n\n"
    
    for i, proxy in enumerate(selected, 1):
        short_link = proxy[:60] + "..." if len(proxy) > 60 else proxy
        text += f"{i}. `{short_link}`\n\n"
    
    text += "👇 **Кнопка connect после каждого прокси!**"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer("✅ Прокси готовы!")

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    help_text = (
        "ℹ️ **Инфо:**\n\n"
        "🔗 **Кнопки:** connect = tg://proxy\n\n"
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
