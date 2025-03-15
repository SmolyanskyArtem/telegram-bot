# ✅ Финальный оптимизированный Telegram-бот с расписанием, уведомлениями, редактированием событий, загрузкой фото и меню

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from flask import Flask
import threading
import aiohttp
import asyncio
from datetime import datetime, timedelta

API_TOKEN = '7611163614:AAE1yTRv2Ru2m6MJdPPVqxa-QxwlhPqK164'
YANDEX_TOKEN = "y0__xDvmIfUARiZ-zUg8YLnwhIIFJ4hykLjwRndz7zE15B_IPFYkw"

bot = Bot(token=API_TOKEN, parse_mode='Markdown')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()

user_ids = set()
category_by_user = {}
user_last_location = {}
CATEGORY_OVERPASS = {
    "toilets": "amenity=toilets",
    "attraction": "tourism=attraction"
}
schedule = [
    {"дата": "2025-03-16", "время": "", "активность": "Прогулка по площади Капитолия и музеям", "место": "Капитолий", "ссылка": "https://www.google.com/maps?q=Capitoline+Hill,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-16", "время": "", "активность": "Обед", "место": "Pasta Chef Monti", "ссылка": "https://www.google.com/maps?q=Pasta+Chef+Monti,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-16", "время": "15:30", "активность": "Колизей, Римский форум и Палатин", "место": "Колизей", "ссылка": "https://www.google.com/maps?q=Колизей,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/xyeIkcyScxrwPw"},
    {"дата": "2025-03-16", "время": "", "активность": "Визит в Giolitti", "место": "Giolitti", "ссылка": "https://maps.app.goo.gl/WX9HLF6VAxmd4mpQ8", "билеты": ""},
    {"дата": "2025-03-16", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-17", "время": "", "активность": "Прогулка по площади Капитолия и музеям", "место": "Капитолий", "ссылка": "https://www.google.com/maps?q=Capitoline+Hill,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-17", "время": "", "активность": "Обед", "место": "Pasta Chef Monti", "ссылка": "https://www.google.com/maps?q=Pasta+Chef+Monti,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-17", "время": "15:30", "активность": "Колизей, Римский форум и Палатин", "место": "Колизей", "ссылка": "https://www.google.com/maps?q=Колизей,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/xyeIkcyScxrwPw"},
    {"дата": "2025-03-17", "время": "", "активность": "Визит в Giolitti", "место": "Giolitti", "ссылка": "https://maps.app.goo.gl/WX9HLF6VAxmd4mpQ8", "билеты": ""},
    {"дата": "2025-03-17", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},

    {"дата": "2025-03-15", "время": "", "активность": "Прогулка по площади Капитолия и музеям", "место": "Капитолий", "ссылка": "https://www.google.com/maps?q=Capitoline+Hill,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-15", "время": "", "активность": "Обед", "место": "Pasta Chef Monti", "ссылка": "https://www.google.com/maps?q=Pasta+Chef+Monti,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-15", "время": "15:30", "активность": "Колизей, Римский форум и Палатин", "место": "Колизей", "ссылка": "https://www.google.com/maps?q=Колизей,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/xyeIkcyScxrwPw"},
    {"дата": "2025-03-15", "время": "", "активность": "Визит в Giolitti", "место": "Giolitti", "ссылка": "https://maps.app.goo.gl/WX9HLF6VAxmd4mpQ8", "билеты": ""},
    {"дата": "2025-03-15", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    
    {"дата": "2025-03-22", "время":"весь день" "", "активность": "Летим в Рим!!!", "место": "Волгоград-Москва-Ереван-Рим", "ссылка": "", "билеты": ""},
    {"дата": "2025-03-22", "время":"18:00" "", "активность": "Ужинаем в Ереване", "место": "Ktoor", "ссылка": "", "билеты": ""},
    {"дата": "2025-03-23", "время": "", "активность": "Прогулка по центру Рима: Пьяцца Навона, Испанская лестница", "место": "Пьяцца Навона", "ссылка": "https://www.google.com/maps?q=Spanish+Steps,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-23", "время": "", "активность": "Обед", "место": "Mariuccia", "ссылка": "https://maps.app.goo.gl/saXjmZhuVRi3rRke6", "билеты": ""},
    {"дата": "2025-03-23", "время": "", "активность": "Фонтан Треви и Пантеон", "место": "Пантеон", "ссылка": "https://www.google.com/maps?q=Trevi+Fountain,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-23", "время": "", "активность": "Mr. 100 Tiramisù", "место": "Mr. 100 Tiramisù", "ссылка": "https://www.google.com/maps?q=Mr.+100+Tiramisù,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-23", "время": "19:00", "активность": "Ужин в честь начала путешествия", "место": "Taverna Romana", "ссылка": "https://www.google.com/maps?q=Taverna+Romana,+Rome,+Italy", "билеты": "link"},
    {"дата": "2025-03-24", "время": "", "активность": "Прогулка по площади Капитолия и музеям", "место": "Капитолий", "ссылка": "https://www.google.com/maps?q=Capitoline+Hill,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-24", "время": "", "активность": "Обед", "место": "Pasta Chef Monti", "ссылка": "https://www.google.com/maps?q=Pasta+Chef+Monti,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-24", "время": "15:30", "активность": "Колизей, Римский форум и Палатин", "место": "Колизей", "ссылка": "https://www.google.com/maps?q=Колизей,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/xyeIkcyScxrwPw"},
    {"дата": "2025-03-24", "время": "", "активность": "Визит в Giolitti", "место": "Giolitti", "ссылка": "https://maps.app.goo.gl/WX9HLF6VAxmd4mpQ8", "билеты": ""},
    {"дата": "2025-03-24", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-25", "время": "", "активность": "Прогулка", "место": "-", "ссылка": "-", "билеты": ""},
    {"дата": "2025-03-25", "время": "", "активность": "Обед", "место": "200 Gradi", "ссылка": "https://www.google.com/maps?q=200+Gradi,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-25", "время": "", "активность": "Замок Святого Ангела", "место": "Замок Святого Ангела", "ссылка": "https://www.google.com/maps?q=Замок+Святого+Ангела,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-25", "время": "", "активность": "Прогулка по площади Святого Петра", "место": "Площадь Святого Петра", "ссылка": "https://www.google.com/maps?q=Площадь+Святого+Петра,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-25", "время": "16:00", "активность": "Ватикан и Сикстинская капелла", "место": "Ватикан", "ссылка": "https://maps.app.goo.gl/cApurj1UUDGV1f8HA", "билеты": "https://disk.yandex.ru/d/_EWbjt_UuvHzUA"},
    {"дата": "2025-03-25", "время": "", "активность": "Визит в Giolitti", "место": "Giolitti", "ссылка": "https://maps.app.goo.gl/WX9HLF6VAxmd4mpQ8", "билеты": ""},
    {"дата": "2025-03-25 00:00:00", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-26", "время": "08:10", "активность": "Выезд во Флоренцию", "место": "Ж/д вокзал", "ссылка": "https://maps.app.goo.gl/f75WGFD5yykKfj237", "билеты": "https://disk.yandex.ru/d/9HIElG56tOcSMQ"},
    {"дата": "2025-03-26", "время": "", "активность": "Завтрак", "место": "All’Antico Vinaio", "ссылка": "https://maps.app.goo.gl/KyLG2EEeFv9RuJk16", "билеты": ""},
    {"дата": "2025-03-26", "время": "", "активность": "Музей со статуей Давида", "место": "Музей академии", "ссылка": "https://www.google.com/maps?q=Музей+академии,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-26", "время": "13:00", "активность": "Обед", "место": "Ristorante Natalino", "ссылка": "https://www.google.com/maps?q=Ristorante+Natalino,+Florence,+Italy", "билеты": "link"},
    {"дата": "2025-03-26", "время": "", "активность": "Прогулка по площади Микеланджело и розовому саду", "место": "Площадь Микеланджело", "ссылка": "https://www.google.com/maps?q=Площадь+Микеланджело,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-26", "время": "", "активность": "Прогулка по площади Синьории и мосту Понте Веккьо", "место": "Понте Веккьо", "ссылка": "https://www.google.com/maps?q=Ponte+Vecchio,+Florence,+Italy", "билеты": ""},
    {"дата": "2025-03-26", "время": "20:14", "активность": "Возвращение в Рим", "место": "Ж/д вокзал", "ссылка": "https://maps.app.goo.gl/yavmHv3zUBGC6hnt6", "билеты": "https://disk.yandex.ru/d/9HIElG56tOcSMQ"},
    {"дата": "2025-03-26 00:00:00", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-27", "время": "", "активность": "Пантеон и прогулка", "место": "Пантеон", "ссылка": "https://www.google.com/maps?q=Pantheon,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-27", "время": "", "активность": "Обед", "место": "Ginger Sapori e Salute", "ссылка": "https://www.google.com/maps?q=Ginger+Sapori+e+Salute,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-27", "время": "17:00", "активность": "Вилла Боргезе", "место": "Villa Borghese", "ссылка": "https://www.google.com/maps?q=Villa+Borghese,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/0Dw5oLUpnFVWkg"},
    {"дата": "2025-03-27", "время": "", "активность": "Mr. 100 Tiramisù", "место": "Mr. 100 Tiramisù", "ссылка": "https://www.google.com/maps?q=Mr.+100+Tiramis%C3%B9,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-27 00:00:00", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-28", "время": "", "активность": "Прогулка по Трастевере", "место": "Трастевере", "ссылка": "https://www.google.com/maps?q=Трастевере,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-28", "время": "", "активность": "Обед", "место": "Dar Poeta", "ссылка": "https://www.google.com/maps?q=Dar+Poeta,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-28", "время": "", "активность": "Холм Яникул", "место": "Холм Яникул", "ссылка": "https://www.google.com/maps?q=Холм+Яникул,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-28", "время": "", "активность": "Базилика Санта-Мария-ин-Трастевере", "место": "Базилика Санта-Мария-ин-Трастевере", "ссылка": "https://www.google.com/maps?q=Базилика+Санта-Мария-ин-Трастевере,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-28 00:00:00", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-29", "время": "06:55", "активность": "Поездка в Венецию", "место": "Ж/д вокзал", "ссылка": "https://www.google.com/maps?q=Ж/д+вокзал,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/3nol-WEp_lg29w"},
    {"дата": "2025-03-29", "время": "", "активность": "Дворец Дожей", "место": "Дворец Дожей", "ссылка": "https://www.google.com/maps?q=Дворец+Дожей,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-29", "время": "", "активность": "Прогулка на гондоле", "место": "Каналы Венеции", "ссылка": "https://www.google.com/maps?q=Каналы+Венеции,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-29", "время": "", "активность": "Посещение могилы Тициана", "место": "Базилика Санта-Мария-Глориоза-дей-Фрари", "ссылка": "https://www.google.com/maps?q=Базилика+Санта-Мария-Глориоза-дей-Фрари,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-29", "время": "", "активность": "Прогулка по мосту Риальто и Каналу Гранде", "место": "Мост Риальто", "ссылка": "https://www.google.com/maps?q=Мост+Риальто,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-29", "время": "", "активность": "Обед", "место": "Dal Moro’s Fresh Pasta", "ссылка": "https://www.google.com/maps?q=Dal+Moro’s+Fresh+Pasta,+Venice,+Italy", "билеты": ""},
    {"дата": "2025-03-29", "время": "18:05", "активность": "Возвращение в Рим", "место": "Ж/д вокзал", "ссылка": "https://www.google.com/maps?q=Ж/д+вокзал,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/3nol-WEp_lg29w"},
    {"дата": "2025-03-29", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-30 00:00:00", "время": "", "активность": "Прогулка и шопинг", "место": "-", "ссылка": "-", "билеты": ""},
    {"дата": "2025-03-30 00:00:00", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-04-02", "время": "", "активность": "Свободное утро", "место": "-", "ссылка": "-", "билеты": ""},
    {"дата": "2025-04-02", "время": "", "активность": "Финальные покупки / прогулка", "место": "-", "ссылка": "-", "билеты": ""},
    {"дата": "2025-04-02", "время": "19:00", "активность": "Ужин в Osteria da Fortunata", "место": "Osteria da Fortunata", "ссылка": "https://www.google.com/maps?q=Osteria+da+Fortunata,+Rome,+Italy", "билеты": "link"},
    {"дата": "2025-04-03 00:00:00", "время": "2025-03-15 07:30:00", "активность": "Переезд в Милан", "место": "Ж/д вокзал", "ссылка": "https://www.google.com/maps?q=Ж/д+вокзал,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/xy3rb_W9wDV4Pg"},
    {"дата": "2025-04-03 00:00:00", "время": "", "активность": "Вылет из Милана", "место": "Аэропорт", "ссылка": "https://maps.app.goo.gl/3TCwfSSbps1spV1d8", "билеты": ""},
]

# Flask keep-alive
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"
def run_flask():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.start()

# Главное меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
main_menu.add(KeyboardButton("📅 Расписание"), KeyboardButton("📍 Что рядом"))
main_menu.add(KeyboardButton("📸 Загрузить фото"), KeyboardButton("🗺 Маршрут до квартиры"))

# Подменю
schedule_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
schedule_menu.add(KeyboardButton("📅 Сегодня"), KeyboardButton("📅 Завтра"))
schedule_menu.add(KeyboardButton("📆 Расписание на дату"), KeyboardButton("⬅ Назад в меню"))

nearby_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
nearby_menu.add(KeyboardButton("🚻 Найти туалет"), KeyboardButton("🏛 Найти достопримечательности"))
nearby_menu.add(KeyboardButton("⬅ Назад в меню"))

# Обработчики меню
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_ids.add(message.from_user.id)
    await message.answer("Бот запущен. Выберите действие:", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "📅 Расписание")
async def open_schedule_menu(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=schedule_menu)

@dp.message_handler(lambda m: m.text == "📍 Что рядом")
async def open_nearby_menu(message: types.Message):
    await message.answer("Выберите категорию:", reply_markup=nearby_menu)

@dp.message_handler(lambda m: m.text == "⬅ Назад в меню")
async def back_to_main_menu(message: types.Message):
    await message.answer("📋 Главное меню:", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "📅 Сегодня")
async def send_today(message: types.Message):
    await send_plan_for_date(message, datetime.now(timezone("Europe/Rome")).date().isoformat(), "📅 Расписание на сегодня")

@dp.message_handler(lambda m: m.text == "📅 Завтра")
async def send_tomorrow(message: types.Message):
    date = (datetime.now(timezone("Europe/Rome")).date() + timedelta(days=1)).isoformat()
    await send_plan_for_date(message, date, "📅 План на завтра")

@dp.message_handler(lambda m: m.text == "📆 Расписание на дату")
async def ask_date(message: types.Message):
    await message.answer("Введите дату в формате ГГГГ-ММ-ДД:")

@dp.message_handler(lambda m: m.text and len(m.text) == 10 and m.text.count('-') == 2)
async def date_input(message: types.Message):
    try:
        date_str = message.text.strip()
        datetime.strptime(date_str, "%Y-%m-%d")
        await send_plan_for_date(message, date_str, f"📅 Расписание на {date_str}")
    except:
        await message.answer("❌ Неверный формат. Пример: 2025-03-25")

async def send_plan_for_date(message, date_str, title):
    plan = [s for s in schedule if s["дата"] == date_str]
    if not plan:
        await message.answer(f"На {date_str} событий нет.")
    else:
        text = f"{title}:\n"
        for s in plan:
            text += f"\n🕘 {s['время']} — {s['активность']} ({s['место']})"
            if s["ссылка"]:
                text += f" → [локация]({s['ссылка']})"
            if s["билеты"]:
                text += f" 🎟 [билеты]({s['билеты']})"
        await message.answer(text, disable_web_page_preview=True)

@dp.message_handler(lambda m: m.text == "❓ Помощь с ботом")
async def help_message(message: types.Message):
    text = (
        "👋 *Как пользоваться ботом:*\n\n"
        "📅 *Сегодня / Завтра* — план на день\n"
        "📆 *Расписание на дату* — введите дату в формате 2025-03-15\n"
        "🚻 / 🏛 — найти объекты рядом (нужна локация)\n"
        "📸 — загрузка фото на Яндекс.Диск\n"
        "⬅ — вернуться в меню"
    )
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("⬅ Назад в меню"))
    await message.answer(text, parse_mode='Markdown', reply_markup=keyboard)

# ✅ Обновлённая функция — ссылки на карты без запроса локации
@dp.message_handler(lambda m: m.text == "🚻 Найти туалет")
async def send_toilet_map(message: types.Message):
    url = "https://www.google.com/maps/search/туалеты/"
    await message.answer(f"🔍 Вот что я нашёл рядом:\n[Открыть карту с туалетами]({url})", parse_mode='Markdown')

@dp.message_handler(lambda m: m.text == "🏛 Найти достопримечательности")
async def send_attraction_map(message: types.Message):
    url = "https://www.google.com/maps/search/достопримечательности/"
    await message.answer(f"🔍 Вот что я нашёл рядом:\n[Открыть карту с достопримечательностями]({url})", parse_mode='Markdown')
# 🗺 Обработчик кнопки "Маршрут до квартиры"
@dp.message_handler(lambda m: m.text == "🗺 Маршрут до квартиры")
async def send_route_to_apartment(message: types.Message):
    apartment_address = "Via degli Etruschi, 3, Rome"
    link = f"https://www.google.com/maps/dir/?api=1&destination={apartment_address.replace(' ', '+')}"
    await message.answer(f"🗺 Вот маршрут до квартиры:\n[Открыть карту]({link})", disable_web_page_preview=True)
    
# Загрузка фото
upload_success_count = {}
delayed_tasks = {}

@dp.message_handler(lambda m: m.text == "📸 Загрузить фото")
async def upload_photo_instruction(message: types.Message):
    await message.answer("Отправьте фото — я загружу их на Яндекс.Диск.")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    file_name = f"user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    upload_url_api = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}
    params = {"path": f"/telegramphotos/{file_name}", "overwrite": "true"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(upload_url_api, headers=headers, params=params) as resp:
                data = await resp.json()
                upload_url = data.get("href")
                if not upload_url:
                    await message.answer("Не удалось получить ссылку загрузки")
                    return
            async with session.get(file_url) as file_resp:
                file_bytes = await file_resp.read()
                async with session.put(upload_url, data=file_bytes) as up:
                    if up.status == 201:
                        await message.delete()
                        upload_success_count[user_id] = upload_success_count.get(user_id, 0) + 1
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
    if user_id in delayed_tasks:
        delayed_tasks[user_id].cancel()
    async def confirm():
        await asyncio.sleep(2)
        count = upload_success_count.get(user_id, 0)
        if count:
            await bot.send_message(user_id, f"✅ Загружено {count} фото на Яндекс.Диск.", reply_markup=main_menu)
            upload_success_count[user_id] = 0
    task = asyncio.create_task(confirm())
    delayed_tasks[user_id] = task

# Автоуведомления
async def send_daily():
    for uid in user_ids:
        await send_today(types.Message(message_id=0, chat=types.Chat(id=uid, type='private')))
async def send_tomorrow_summary():
    for uid in user_ids:
        await send_tomorrow(types.Message(message_id=0, chat=types.Chat(id=uid, type='private')))
async def check_reminders():
    now = datetime.now(timezone("Europe/Rome"))
    for s in schedule:
        if not s.get("билеты"): continue
        try:
            evt = timezone("Europe/Rome").localize(datetime.strptime(f"{s['дата']} {s['время']}", "%Y-%m-%d %H:%M"))
            secs = (evt - now).total_seconds()
            for uid in user_ids:
                if 3540 < secs < 3660:
                    await bot.send_message(uid, f"⏰ Напоминание: через 1 час — {s['активность']} ({s['место']})")
                elif 1740 < secs < 1860:
                    await bot.send_message(uid, f"⏰ Скоро: через 30 минут — {s['активность']} ({s['место']})")
        except: continue
async def on_startup(dp):
    keep_alive()
    rome = timezone("Europe/Rome")
    scheduler.add_job(send_daily, 'cron', hour=8, timezone=rome)
    scheduler.add_job(send_tomorrow_summary, 'cron', hour=20, timezone=rome)
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
