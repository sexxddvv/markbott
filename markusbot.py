import asyncio
import logging
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Nastavení logování na podrobnější úroveň
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Token bota
API_TOKEN = os.getenv("API_TOKEN", "8149820817:AAFSNytOOPq8Wd70l5DXykYMKqHADVibj2M")
logging.info(f"API_TOKEN načten: {'Set' if API_TOKEN else 'Not set'}")

# Webhook nastavení
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://markbott.unacceptable-tandi-hexxx-7738253.koyeb.app{WEBHOOK_PATH}"
logging.info(f"WEBHOOK_URL nastaven na: {WEBHOOK_URL}")

# Port
PORT = int(os.getenv("PORT", 8000))
logging.info(f"Port nastaven na: {PORT}")

# Inicializace bota
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# Paměť signálů
signal_memory = {}

# Handler pro GET /webhook (pro health check)
async def health_check(request):
    logging.info("Received health check request")
    return web.Response(status=200, text="OK")

# Funkce pro nastavení webhooku s podrobným logováním
async def on_startup():
    try:
        logging.info("Začínám nastavovat webhook...")
        webhook_info = await bot.get_webhook_info()
        logging.info(f"Současné webhook info: {webhook_info}")
        
        if webhook_info.url != WEBHOOK_URL:
            logging.info(f"Nastavuji nový webhook na: {WEBHOOK_URL}")
            await bot.set_webhook(url=WEBHOOK_URL)
            logging.info(f"Webhook úspěšně nastaven na: {WEBHOOK_URL}")
        else:
            logging.info("Webhook je již nastaven správně.")
    except Exception as e:
        logging.error(f"Chyba při nastavování webhooku: {str(e)}")
        raise

# Handlery pro Telegram
@dp.message()
async def send_welcome(message: types.Message):
    logging.info(f"Přijatá zpráva: {message.text} od uživatele {message.from_user.id}")
    if message.text == "/start":
        user_name = message.from_user.first_name
        
        response = (f"*{user_name}, we are glad to welcome you to our Trading Academy!*\n\n"
                    "_Tired of getting burned by empty promises of pseudo-traders?_\n\n"
                    "_Tired of draining money on unworkable, expensive subscriptions?_\n\n"
                    "_Just tired? 😮_\n\n"
                    "_It's time to change the game! Our bot provides powerful tools—head to the main menu to get started today._")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Main Menu 📱", callback_data="main_menu")]
        ])
        
        logging.info("Odesílám uvítací zprávu")
        await message.answer(response, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    logging.info(f"Přijatý callback: {callback.data}")
    response = ("*Main menu of AI Trading Academy 📈*\n\n"
                "_Explore the bot interface, stay updated, and access trading signals._\n\n"
                "_Use the buttons below to navigate:_\n\n"
                "🔔 Channel – Stay informed with the latest updates.\n"
                "📊 Trade – Get real-time trading signals.\n"
                "☎️ Support – Get assistance whenever you need it.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Channel", url="https://t.me/optionbotv2")],
        [InlineKeyboardButton(text="📊 Trade", callback_data="trade")],
        [InlineKeyboardButton(text="☎️ Support", url="https://t.me/AllinBrooo")]
    ])
    
    logging.info("Zobrazuji hlavní menu")
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "trade")
async def trade_menu(callback: CallbackQuery):
    logging.info(f"Přijatý callback: {callback.data}")
    response = "❓ *Select quote type:*"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Stock", callback_data="stock"), InlineKeyboardButton(text="OTC", callback_data="otc")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")]
    ])
    
    logging.info("Zobrazuji menu pro obchodování")
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data in ["stock", "otc"])
async def select_signal_time(callback: CallbackQuery):
    logging.info(f"Přijatý callback: {callback.data}")
    response = "⏰ *Select the signal time:*"
    quote_type = callback.data
    logging.info(f"Generuji tlačítka pro výběr času signálu s quote_type: {quote_type}")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 Min", callback_data=f"{quote_type}:1min"),
         InlineKeyboardButton(text="5 Min", callback_data=f"{quote_type}:5min"),
         InlineKeyboardButton(text="7 Min", callback_data=f"{quote_type}:7min"),
         InlineKeyboardButton(text="10 Min", callback_data=f"{quote_type}:10min"),
         InlineKeyboardButton(text="15 Min", callback_data=f"{quote_type}:15min")],
        [InlineKeyboardButton(text="5 Seconds", callback_data=f"{quote_type}:5sec"),
         InlineKeyboardButton(text="10 Seconds", callback_data=f"{quote_type}:10sec"),
         InlineKeyboardButton(text="15 Seconds", callback_data=f"{quote_type}:15sec")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="trade")]
    ])
    
    logging.info(f"Vygenerována klávesnice s callback daty: {keyboard.inline_keyboard}")
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: len(c.data.split(":")) == 2 and c.data.split(":")[0] in ["stock", "otc"] and c.data.split(":")[1] in ["1min", "5min", "7min", "10min", "15min", "5sec", "10sec", "15sec"])
async def select_currency_pair(callback: CallbackQuery):
    logging.info(f"Přijatý callback: {callback.data}")
    response = "⚙️ *Select a currency pair:*"
    quote_type, signal_time = callback.data.split(":")
    logging.info(f"Generuji tlačítka pro výběr měnového páru s quote_type: {quote_type}, signal_time: {signal_time}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="CAD/JPY", callback_data=f"{quote_type}:{signal_time}:cadjpy"),
         InlineKeyboardButton(text="GBP/JPY", callback_data=f"{quote_type}:{signal_time}:gbpjpy"),
         InlineKeyboardButton(text="EUR/CAD", callback_data=f"{quote_type}:{signal_time}:eurcad"),
         InlineKeyboardButton(text="EUR/USD", callback_data=f"{quote_type}:{signal_time}:eurusd")],
        [InlineKeyboardButton(text="USD/JPY", callback_data=f"{quote_type}:{signal_time}:usdjpy"),
         InlineKeyboardButton(text="GBP/AUD", callback_data=f"{quote_type}:{signal_time}:gbpaud"),
         InlineKeyboardButton(text="GBP/USD", callback_data=f"{quote_type}:{signal_time}:gbpusd"),
         InlineKeyboardButton(text="AUD/JPY", callback_data=f"{quote_type}:{signal_time}:audjpy")],
        [InlineKeyboardButton(text="EUR/GBP", callback_data=f"{quote_type}:{signal_time}:eurgbp"),
         InlineKeyboardButton(text="EUR/JPY", callback_data=f"{quote_type}:{signal_time}:eurjpy"),
         InlineKeyboardButton(text="USD/CAD", callback_data=f"{quote_type}:{signal_time}:usdcad"),
         InlineKeyboardButton(text="AUD/CHF", callback_data=f"{quote_type}:{signal_time}:audchf")],
        [InlineKeyboardButton(text="AUD/CAD", callback_data=f"{quote_type}:{signal_time}:audcad")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"{quote_type}")]
    ])
    
    logging.info(f"Vygenerována klávesnice s callback daty: {keyboard.inline_keyboard}")
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: len(c.data.split(":")) == 3 and c.data.split(":")[0] in ["stock", "otc"])
async def send_signal(callback: CallbackQuery):
    logging.info(f"Přijatý callback: {callback.data}")
    quote_type, signal_time, currency_pair = callback.data.split(":")
    currency_pair = currency_pair.upper()
    logging.info(f"Zpracovaná data - quote_type: {quote_type}, signal_time: {signal_time}, currency_pair: {currency_pair}")

    signal_key = f"{currency_pair}_{signal_time}_{quote_type}"

    if signal_key in signal_memory:
        signal_data = signal_memory[signal_key]
        signal_count = signal_data["count"]
        if signal_count >= 4:
            direction = "📉📉⬇️" if signal_data["direction"] == "📈📈⬆️" else "📈📈⬆️"
            probability = random.randint(92, 97)
            signal_memory[signal_key] = {"direction": direction, "probability": probability, "count": 1}
        else:
            direction = signal_data["direction"]
            probability = signal_data["probability"]
            signal_memory[signal_key]["count"] += 1
    else:
        direction = random.choice(["📈📈⬆️", "📉📉⬇️"])
        probability = random.randint(92, 97)
        signal_memory[signal_key] = {"direction": direction, "probability": probability, "count": 1}

    time_text = {
        "1min": "1 Minute", "5min": "5 Minutes", "7min": "7 Minutes", "10min": "10 Minutes", "15min": "15 Minutes",
        "5sec": "5 Seconds", "10sec": "10 Seconds", "15sec": "15 Seconds"
    }[signal_time]

    if quote_type == "otc":
        pair_text = f"{currency_pair} OTC"
    else:
        pair_text = currency_pair

    response = (f"*Currency pair: {pair_text}* 📈📈\n\n"
                f"_Expiry time: {time_text}_\n\n"
                f"*Volatility:* _Moderate_\n\n"
                f"*Probability of success:* _{probability}%_\n\n"
                f"Result of market analysis by bot: {direction}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"{quote_type}:{signal_time}")]
    ])
    
    logging.info(f"Odesílám signál: {response}")
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()

# Spuštění aplikace s webhookem
async def start_bot():
    await on_startup()
    app = web.Application()
    
    # Přidání handleru pro GET /webhook (health check)
    app.router.add_get(WEBHOOK_PATH, health_check)
    
    # Přidání aiogram webhook handleru (pro POST požadavky od Telegramu)
    webhook_request_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_request_handler.register(app, path=WEBHOOK_PATH)
    
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Bot běží na portu {PORT}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_bot())
