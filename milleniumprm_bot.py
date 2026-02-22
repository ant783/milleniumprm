import asyncio
import random
import aiohttp
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ BOT_TOKEN ХРАНИТСЯ ПРЯМО В ЭТОМ ФАЙЛЕ
BOT_TOKEN = "8275812174:AAEY3EDh3KTvA1XrgCAnD19QaJcPxWMWQTU"  # ← ЗАМЕНИТЕ НА СВОЙ

PROXY_URL = 'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt'

# Проверка токена
if not BOT_TOKEN or BOT_TOKEN == "7769789234:AAFGawI5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k5k":
    print("❌ ОШИБКА: Замените BOT_TOKEN на ваш реальный токен!")
    exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранилище лимитов: {user_id: last_update_time}
user_limits = {}

async def fetch_proxies():
    """Загружает список прокси из файла"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    proxies = [line.strip() for line in content.splitlines() if line.strip()]
                    logger.info(f"Загружено {len(proxies)} прокси")
                    return proxies
    except Exception as e:
        logger.error(f"Ошибка загрузки прокси: {e}")
    return []

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить прокси", callback_data="update_proxies")]
    ])
    welcome_text = (
        "👋 **Добро пожаловать в Бесплатные proxy для Telegram!**\n\n"
        "🔥 Получите 3 случайных **MTProto прокси** для обхода блокировок.\n\n"
        "⚡ **Как использовать:**\n"
        "1️⃣ Нажмите кнопку «Обновить прокси»\n"
        "2️⃣ Выберите прокси и нажмите «🔗 Подключиться»\n"
        "3️⃣ Telegram автоматически подключится\n\n"
        "⏰ Доступно **1 раз в сутки** на пользователя"
    )
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "update_proxies")
async def update_proxies(callback: types.CallbackQuery):
    """Обработчик кнопки обновить прокси"""
    user_id = callback.from_user.id
    now = datetime.now()
    
    # Проверка лимита (24 часа)
    last_update = user_limits.get(user_id)
    if last_update and now - last_update < timedelta(days=1):
        time_left = timedelta(days=1) - (now - last_update)
        hours = int(time_left.total_seconds() // 3600)
        mins = int((time_left.total_seconds() % 3600) // 60)
        await callback.answer(f"⏳ Подождите {hours}ч {mins}м до следующего обновления!")
        return
    
    # Показываем "Загрузка..."
    await callback.message.edit_text("⏳ Загружаем свежие прокси...")
    
    # Загружаем прокси
    proxies = await fetch_proxies()
    if not proxies:
        await callback.message.edit_text(
            "❌ Не удалось загрузить прокси.\n"
            "🔄 Попробуйте позже или проверьте интернет."
        )
        return
    
    if len(proxies) < 3:
        await callback.message.edit_text("❌ Недостаточно прокси в списке.")
        return
    
    # Выбираем 3 случайных прокси
    selected = random.sample(proxies, 3)
    
    # Создаем клавиатуру с кнопками "Подключиться"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for proxy in selected:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="🔗 Подключиться", url=proxy)
        ])
    
    # Формируем текст с короткими превью
