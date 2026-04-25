import os
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from config import Config
from services.db import init_db, add_user_if_not_exists, set_user_topics, get_user_topics, set_active_status, get_all_subscribers
from services.parser import get_latest_news
from services.llm_agent import filter_and_summarize

logging.basicConfig(level=logging.INFO)

init_db()

# Читаем адрес из .env, если его там нет — используем адрес для Docker
proxy_url = os.getenv("PROXY_URL", "http://host.docker.internal:12334")
session = AiohttpSession(proxy=proxy_url)
bot = Bot(token=Config.TELEGRAM_TOKEN, session=session)
dp = Dispatcher()

# --- ФУНКЦИЯ РАССЫЛКИ (ПО ЗАПРОСУ И ПО ТАЙМЕРУ) ---
async def process_news_for_user(user_id, topics):
    await bot.send_message(user_id, f"📰 Готовлю дайджест по темам: {', '.join(topics)}...")
    raw_news = get_latest_news(limit_per_feed=10).split("\n\n---\n\n")
    
    found_count = 0
    for item in raw_news:
        if not item.strip(): continue
        
        result = await filter_and_summarize(item, topics)
        if result and result != "SKIP":
            await bot.send_message(user_id, result)
            found_count += 1
            await asyncio.sleep(1) # Защита от лимитов Telegram

    if found_count == 0:
        await bot.send_message(user_id, "Ничего нового по твоим темам пока нет.")

# --- УТРЕННЯЯ РАССЫЛКА (ПЛАНИРОВЩИК) ---
async def morning_digest():
    logging.info("⏰ Запуск утренней рассылки...")
    subscribers = get_all_subscribers()
    for user_id, topics_str in subscribers:
        topics = topics_str.split(",")
        try:
            await process_news_for_user(user_id, topics)
        except Exception as e:
            logging.error(f"Ошибка отправки юзеру {user_id}: {e}")

# --- ОБРАБОТЧИКИ КОМАНД ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user_if_not_exists(message.from_user.id)
    await message.answer(
        "Привет, Степан! Я AI Postman.\n"
        "Напиши темы через запятую (например: ЧАЗН, космос, мини ПК).\n\n"
        "Управление рассылкой:\n"
        "🔔 /subscribe - Включить дайджест (в 09:00)\n"
        "🔕 /unsubscribe - Выключить дайджест\n"
        "🔎 /check - Проверить новости прямо сейчас"
    )

@dp.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    add_user_if_not_exists(message.from_user.id)
    set_active_status(message.from_user.id, 1)
    await message.answer("🔔 Рассылка включена! Жди новости по утрам.")

@dp.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    add_user_if_not_exists(message.from_user.id)
    set_active_status(message.from_user.id, 0)
    await message.answer("🔕 Рассылка отключена.")

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    add_user_if_not_exists(message.from_user.id)
    topics = get_user_topics(message.from_user.id)
    if not topics:
        await message.answer("Сначала напиши свои интересы через запятую!")
        return
    await process_news_for_user(message.from_user.id, topics)

@dp.message(F.text)
async def handle_text(message: types.Message):
    add_user_if_not_exists(message.from_user.id)
    text = message.text.strip()
    if "," in text or len(text.split()) < 5:
        topics = [t.strip() for t in text.split(",") if t.strip()]
        set_user_topics(message.from_user.id, topics)
        await message.answer(f"✅ Темы обновлены: {', '.join(topics)}")

# --- СТАРТ БОТА ---
async def main():
    # Настраиваем планировщик из Лунохода
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(morning_digest, 'cron', hour=9, minute=0)
    scheduler.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот выключен")