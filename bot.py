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

    {"дата": "2025-03-17", "время": "", "активность": "Прогулка по площади Капитолия и музеям", "место": "Капитолий", "ссылка": "https://www.google.com/maps?q=Capitoline+Hill,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-17", "время": "", "активность": "Обед", "место": "Pasta Chef Monti", "ссылка": "https://www.google.com/maps?q=Pasta+Chef+Monti,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-17", "время": "15:30", "активность": "Колизей, Римский форум и Палатин", "место": "Колизей", "ссылка": "https://www.google.com/maps?q=Колизей,+Rome,+Italy", "билеты": "https://disk.yandex.ru/d/xyeIkcyScxrwPw"},
    {"дата": "2025-03-17", "время": "", "активность": "Визит в Giolitti", "место": "Giolitti", "ссылка": "https://maps.app.goo.gl/WX9HLF6VAxmd4mpQ8", "билеты": ""},
    {"дата": "2025-03-17", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-18", "время": "", "активность": "Прогулка", "место": "-", "ссылка": "-", "билеты": ""},
    {"дата": "2025-03-18", "время": "", "активность": "Обед", "место": "200 Gradi", "ссылка": "https://www.google.com/maps?q=200+Gradi,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-18", "время": "", "активность": "Замок Святого Ангела", "место": "Замок Святого Ангела", "ссылка": "https://www.google.com/maps?q=Замок+Святого+Ангела,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-18", "время": "", "активность": "Прогулка по площади Святого Петра", "место": "Площадь Святого Петра", "ссылка": "https://www.google.com/maps?q=Площадь+Святого+Петра,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-18", "время": "16:00", "активность": "Ватикан и Сикстинская капелла", "место": "Ватикан", "ссылка": "https://maps.app.goo.gl/cApurj1UUDGV1f8HA", "билеты": "https://disk.yandex.ru/d/_EWbjt_UuvHzUA"},
    {"дата": "2025-03-18", "время": "", "активность": "Визит в Giolitti", "место": "Giolitti", "ссылка": "https://maps.app.goo.gl/WX9HLF6VAxmd4mpQ8", "билеты": ""},
    {"дата": "2025-03-18 00:00:00", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    {"дата": "2025-03-19", "время": "08:10", "активность": "Выезд во Флоренцию", "место": "Ж/д вокзал", "ссылка": "https://maps.app.goo.gl/f75WGFD5yykKfj237", "билеты": "https://disk.yandex.ru/d/9HIElG56tOcSMQ"},
    {"дата": "2025-03-19", "время": "", "активность": "Завтрак", "место": "All’Antico Vinaio", "ссылка": "https://maps.app.goo.gl/KyLG2EEeFv9RuJk16", "билеты": ""},
    {"дата": "2025-03-19", "время": "", "активность": "Музей со статуей Давида", "место": "Музей академии", "ссылка": "https://www.google.com/maps?q=Музей+академии,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-19", "время": "13:00", "активность": "Обед", "место": "Ristorante Natalino", "ссылка": "https://www.google.com/maps?q=Ristorante+Natalino,+Florence,+Italy", "билеты": "link"},
    {"дата": "2025-03-19", "время": "", "активность": "Прогулка по площади Микеланджело и розовому саду", "место": "Площадь Микеланджело", "ссылка": "https://www.google.com/maps?q=Площадь+Микеланджело,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-19", "время": "", "активность": "Прогулка по площади Синьории и мосту Понте Веккьо", "место": "Понте Веккьо", "ссылка": "https://www.google.com/maps?q=Ponte+Vecchio,+Florence,+Italy", "билеты": ""},
    {"дата": "2025-03-19", "время": "20:14", "активность": "Возвращение в Рим", "место": "Ж/д вокзал", "ссылка": "https://maps.app.goo.gl/yavmHv3zUBGC6hnt6", "билеты": "https://disk.yandex.ru/d/9HIElG56tOcSMQ"},
    {"дата": "2025-03-19 00:00:00", "время": "", "активность": "Ужин дома", "место": "Квартира", "ссылка": "https://maps.app.goo.gl/L7VB6bvHHaUJwy89A", "билеты": ""},
    
    {"дата": "2025-03-22", "время":"весь день", "активность": "Летим в Рим!!!", "место": "Волгоград-Москва-Ереван-Рим", "ссылка": "", "билеты": ""},
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
    {"дата": "2025-03-25", "время": "", "активность": "Замок Святого Ангела", "место": "Замок Святого Ангела", "ссылка": "https://www.google.com/maps?q=Замок+Святого+Ангела,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-25", "время": "", "активность": "Прогулка по площади Святого Петра", "место": "Площадь Святого Петра", "ссылка": "https://www.google.com/maps?q=Площадь+Святого+Петра,+Rome,+Italy", "билеты": ""},
    {"дата": "2025-03-25", "время": "", "активность": "Обед", "место": "200 Gradi", "ссылка": "https://www.google.com/maps?q=200+Gradi,+Rome,+Italy", "билеты": ""},
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
    await message.answer("Привет! Я уже готов помочь 🙂 Что делаем?", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "📅 Расписание")
async def open_schedule_menu(message: types.Message):
    await message.answer("Что тебе показать?", reply_markup=schedule_menu)

@dp.message_handler(lambda m: m.text == "📍 Что рядом")
async def open_nearby_menu(message: types.Message):
    await message.answer("Смотри, что могу найти рядом 👇", reply_markup=nearby_menu)

@dp.message_handler(lambda m: m.text == "⬅ Назад в меню")
async def back_to_main_menu(message: types.Message):
    await message.answer("Окей, я снова здесь 😎", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "📅 Сегодня")
async def send_today(message: types.Message):
    await send_plan_for_date(message, datetime.now(timezone("Europe/Rome")).date().isoformat(), "📅 План на сегодня")

@dp.message_handler(lambda m: m.text == "📅 Завтра")
async def send_tomorrow(message: types.Message):
    date = (datetime.now(timezone("Europe/Rome")).date() + timedelta(days=1)).isoformat()
    await send_plan_for_date(message, date, "📅 Завтра в планах")

@dp.message_handler(lambda m: m.text == "📆 Расписание на дату")
async def ask_date(message: types.Message):
    await message.answer("Скинь дату в формате ГГГГ-ММ-ДД, посмотрю план 🧐")

@dp.message_handler(lambda m: m.text and len(m.text) == 10 and m.text.count('-') == 2)
async def date_input(message: types.Message):
    try:
        date_str = message.text.strip()
        datetime.strptime(date_str, "%Y-%m-%d")
        await send_plan_for_date(message, date_str, f"📅 План на {date_str}")
    except:
        await message.answer("Упс! Формат даты не тот. Пример: 2025-03-25")

async def send_plan_for_date(message, date_str, title):
    plan = [s for s in schedule if s["дата"] == date_str]
    if not plan:
        await message.answer(f"Пока на {date_str} ничего нет. Отдохнём? 😌")
    else:
        text = f"{title}:\n"
        for s in plan:
            text += f"\n🕘 {s['время']} — {s['активность']} ({s['место']})"
            if s["ссылка"]:
                text += f" → [локация]({s['ссылка']})"
            if s["билеты"]:
                text += f" 🎟 [билеты]({s['билеты']})"
        await message.answer(text, disable_web_page_preview=True)


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

class AddEventStates(StatesGroup):
    дата = State()
    время = State()
    активность = State()
    место = State()
    ссылка = State()
    билеты = State()

@dp.message_handler(commands=['добавить'])
async def add_event_start(message: types.Message):
    await message.answer("Начнём добавление события! Напиши дату (ГГГГ-ММ-ДД):")
    await AddEventStates.дата.set()

@dp.message_handler(state=AddEventStates.дата)
async def add_event_date(message: types.Message, state: FSMContext):
    await state.update_data(дата=message.text.strip())
    await message.answer("Теперь время (ЧЧ:ММ):")
    await AddEventStates.время.set()

@dp.message_handler(state=AddEventStates.время)
async def add_event_time(message: types.Message, state: FSMContext):
    await state.update_data(время=message.text.strip())
    await message.answer("Как называется активность?")
    await AddEventStates.активность.set()

@dp.message_handler(state=AddEventStates.активность)
async def add_event_activity(message: types.Message, state: FSMContext):
    await state.update_data(активность=message.text.strip())
    await message.answer("Где это будет?")
    await AddEventStates.место.set()

@dp.message_handler(state=AddEventStates.место)
async def add_event_place(message: types.Message, state: FSMContext):
    await state.update_data(место=message.text.strip())
    await message.answer("Скинь ссылку на локацию (или - если нет):")
    await AddEventStates.ссылка.set()

@dp.message_handler(state=AddEventStates.ссылка)
async def add_event_link(message: types.Message, state: FSMContext):
    await state.update_data(ссылка=message.text.strip())
    await message.answer("И ссылку на билеты (или - если нет):")
    await AddEventStates.билеты.set()

@dp.message_handler(state=AddEventStates.билеты)
async def add_event_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_event = {
        "дата": data['дата'],
        "время": data['время'],
        "активность": data['активность'],
        "место": data['место'],
        "ссылка": data['ссылка'] if data['ссылка'] != '-' else "",
        "билеты": message.text.strip() if message.text.strip() != '-' else ""
    }
    schedule.append(new_event)
    await message.answer("Супер! Добавил новое событие ✅")
    await state.finish()

class EventEditStates(StatesGroup):
    choosing_date = State()
    choosing_event = State()
    editing_field = State()
    new_value = State()

@dp.message_handler(commands=['редактировать'])
async def start_edit_event(message: types.Message, state: FSMContext):
    await message.answer("Напиши дату события, которое редактируем (ГГГГ-ММ-ДД):")
    await EventEditStates.choosing_date.set()

@dp.message_handler(state=EventEditStates.choosing_date)
async def choose_event_date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    events = [e for e in schedule if e['дата'] == date_str]
    if not events:
        await message.answer("Хм, ничего не вижу на эту дату. Может, добавим новое событие? Команда /добавить тебе в помощь!")
        await state.finish()
        return
    await state.update_data(date=date_str, events=events)
    event_list = "\n".join([f"{idx+1}. {e['время']} {e['активность']} ({e['место']})" for idx, e in enumerate(events)])
    await message.answer(f"Вот список на {date_str} — выбери номер события для редактирования:\n{event_list}")
    await EventEditStates.choosing_event.set()

@dp.message_handler(state=EventEditStates.choosing_event)
async def choose_event_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        idx = int(message.text.strip()) - 1
        event = data['events'][idx]
        await state.update_data(selected_event_index=idx)
        await message.answer("Что меняем? Напиши: дата, время, активность, место, ссылка или билеты")
        await EventEditStates.editing_field.set()
    except:
        await message.answer("Не могу понять, какой номер ты выбрал. Попробуй ещё раз — просто число из списка!")

@dp.message_handler(state=EventEditStates.editing_field)
async def choose_field(message: types.Message, state: FSMContext):
    field = message.text.strip().lower()
    if field not in ['дата', 'время', 'активность', 'место', 'ссылка', 'билеты']:
        await message.answer("Выбери, что будем менять: дата, время, активность, место, ссылка или билеты")
        return
    await state.update_data(editing_field=field)
    await message.answer(f"Окей, напиши новое значение для {field}:")
    await EventEditStates.new_value.set()

@dp.message_handler(state=EventEditStates.new_value)
async def apply_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    field = data['editing_field']
    value = message.text.strip()
    date = data['date']
    idx = data['selected_event_index']
    for i, e in enumerate(schedule):
        if e['дата'] == date:
            if i == idx:
                schedule[i][field] = value
                break
    await message.answer("Готово! Всё поменял ✨")
    await state.finish()

# ✅ Обновлённая функция: План на сегодня
async def send_today_plan():
    date = datetime.now(timezone("Europe/Rome")).date().isoformat()
    plan = [s for s in schedule if s["дата"] == date]
    if not plan:
        return
    text = f"📅 План на сегодня:\n"
    for s in plan:
        time_part = f"{s['время']} — " if s['время'] else ""
        emoji = "🕐"
        if any(word in s['активность'].lower() for word in ['обед', 'завтрак', 'ужин']):
            emoji = "🍽"
        elif 'прогулка' in s['активность'].lower():
            emoji = "🚶"
        elif 'музей' in s['активность'].lower():
            emoji = "🏛"
        elif any(word in s['активность'].lower() for word in ['поездка', 'выезд', 'переезд']):
            emoji = "🚆"
        elif 'возвращение' in s['активность'].lower():
            emoji = "⬅"
        elif 'giolitti' in s['активность'].lower():
            emoji = "🍨"
        elif 'билеты' in s['активность'].lower():
            emoji = "🎟"
        text += f"\n{emoji} {time_part}{s['активность']} ({s['место']})"
        if s.get("ссылка"):
            text += f" → [локация]({s['ссылка']})"
        if s.get("билеты"):
            text += f" 🎟 [билеты]({s['билеты']})"
    for uid in user_ids:
        await bot.send_message(uid, text, disable_web_page_preview=True)


# ✅ Обновлённая функция: Саммари плана на завтра с эмодзи и временем
async def send_tomorrow_summary():
    date = (datetime.now(timezone("Europe/Rome")).date() + timedelta(days=1)).isoformat()
    plan = [s for s in schedule if s["дата"] == date]
    if not plan:
        return
    summary = ["📌 *День подходит к концу!*", "", "📋 *Коротко про планы на завтра:*"]
    for s in plan:
        emoji = "🕐"
        if any(word in s['активность'].lower() for word in ['обед', 'завтрак', 'ужин']):
            emoji = "🍽"
        elif 'прогулка' in s['активность'].lower():
            emoji = "🚶"
        elif 'музей' in s['активность'].lower():
            emoji = "🏛"
        elif any(word in s['активность'].lower() for word in ['поездка', 'выезд', 'переезд']):
            emoji = "🚆"
        elif 'возвращение' in s['активность'].lower():
            emoji = "⬅"
        elif 'giolitti' in s['активность'].lower():
            emoji = "🍨"
        elif 'билеты' in s['активность'].lower():
            emoji = "🎟"
        time_part = f"{s['время']} — " if s['время'] else ""
        summary.append(f"{emoji} {time_part}{s['активность']}")

 # 🔽 Добавляем выделенный блок-инструкцию про фото
    summary.append("\n📸 *Как сохранить фотографии?*")
    summary.append("1️⃣ Нажмите внизу кнопку *«📸 Загрузить фото»*")
    summary.append("2️⃣ Отправьте свои фотографии прямо сюда")
    summary.append("Я всё аккуратно сохраню на диск.")
    summary.append("\n📂 [Где потом смотреть фотографии — на Яндекс.Диске](https://disk.yandex.ru/d/nrOTg5cbjwywxA)")


    for uid in user_ids:
        await bot.send_message(uid, "\n".join(summary), parse_mode="Markdown", disable_web_page_preview=True)


@dp.message_handler(commands=['тестзавтра'])
async def test_send_tomorrow(message: types.Message):
    await send_tomorrow_summary()
    
# ✅ Уведомления и запуск авторассылок
# Храним id уже отправленных напоминаний, чтобы не дублировать
# Храним ID отправленных напоминаний
sent_reminders = set()

async def check_reminders():
    now = datetime.now(timezone("Europe/Rome"))
    for s in schedule:
        if not s.get("билеты") or not s.get("время"):
            continue
        try:
            event_time = timezone("Europe/Rome").localize(datetime.strptime(f"{s['дата']} {s['время']}", "%Y-%m-%d %H:%M"))
            seconds_until = (event_time - now).total_seconds()

            for uid in user_ids:
                reminder_id_1h = f"{uid}_{s['дата']}_{s['время']}_1h"
                reminder_id_30m = f"{uid}_{s['дата']}_{s['время']}_30m"

                # Общий текст с ссылками (если есть)
                links_text = ""
                if s.get("ссылка"):
                    links_text += f"\n📍 [Локация]({s['ссылка']})"
                if s.get("билеты"):
                    links_text += f"\n🎟 [Билеты]({s['билеты']})"

                # Напоминание за 1 час
                if 3000 < seconds_until < 4200 and reminder_id_1h not in sent_reminders:
                    msg = f"⏰ Напоминание: через 1 час — *{s['активность']}* ({s['место']}){links_text}"
                    await bot.send_message(uid, msg, parse_mode='Markdown', disable_web_page_preview=True)
                    sent_reminders.add(reminder_id_1h)

                # Напоминание за 30 минут
                elif 1500 < seconds_until < 2100 and reminder_id_30m not in sent_reminders:
                    msg = f"⏰ Скоро: через 30 минут — *{s['активность']}* ({s['место']}){links_text}"
                    await bot.send_message(uid, msg, parse_mode='Markdown', disable_web_page_preview=True)
                    sent_reminders.add(reminder_id_30m)

        except Exception as e:
            print(f"[Ошибка напоминания] {e}")

            continue

async def on_startup(dp):
    keep_alive()
    rome = timezone("Europe/Rome")
    scheduler.add_job(send_today_plan, 'cron', hour=8, minute=00, timezone=rome)
    scheduler.add_job(send_tomorrow_summary, 'cron', hour=20, minute=45, timezone=rome)
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
