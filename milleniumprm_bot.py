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
    """Загружает прокси с GitHub"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL_GITHUB, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    proxies = [line.strip() for line in content.splitlines() if line.strip()]
                    logger.info(f"✅ GitHub: Загружено {len(proxies)} прокси")
                    return proxies
    except Exception as e:
        logger.error(f"❌ GitHub недоступен: {e}")
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
    """Загружает прокси с fallback логикой"""
    all_proxies = []
    
    # 1. Пробуем GitHub
    github_proxies = await fetch_proxies_github()
    if github_proxies:
        all_proxies.extend(github_proxies)
        logger.info("✅ Используем GitHub прокси")
        return list(set(all_proxies))  # Удаляем дубли
    
    # 2. Если GitHub недоступен -> mtpro.xyz
    logger.info("🔄 GitHub недоступен, пробуем mtpro.xyz...")
    mtpro_proxies = await fetch_proxies_mtpro()
    if mtpro_proxies:
        all_proxies.extend(mtpro_proxies)
        logger.info("✅ Используем mtpro.xyz прокси")
        return list(set(all_proxies))
    
    # 3. Если mtpro.xyz недоступен -> mtproto-ru
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
    """Обработчик кнопки"""
    await callback.message.edit_text("⏳ Загружаем свежие прокси...")
    
    proxies = await fetch_all_proxies()
    if len(proxies) < 3:
        await callback.message.edit_text("❌ Недостаточно прокси. Попробуйте позже.")
        return
    
    selected = random.sample(proxies, 3)
    
    # Кнопка "connect" ПОСЛЕ КАЖДОГО прокси
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="connect", url=selected[0])],
        [InlineKeyboardButton(text="connect", url=selected[1])],
        [InlineKeyboardButton(text="connect", url=selected[2])]
    ])
    
    text = "🔥 **3 случайных MTProto прокси:**\n\n"
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
