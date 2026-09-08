import asyncio
import logging
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, FSInputFile
from aiogram.enums import ParseMode
from keyboards import (
    get_start_keyboard, 
    get_question3_keyboard, 
    get_final_keyboard,
    get_admin_keyboard,
    get_accepted_keyboard,
    get_main_menu_keyboard,
    get_profile_keyboard,
    get_traffic_keyboard,
    get_traffic_link_keyboard,
    get_payout_keyboard,
    get_payout_admin_keyboard,
    get_payout_screenshot_keyboard,
    get_ton_address_keyboard,
    get_ton_address_list_keyboard
)

BOT_TOKEN = "8327945346:AAEXp_BmRBFNcFL1SkRSUqaMZwaB_WNUyXA"
ADMIN_ID = 922986659
GROUP_ID = -1004475913996

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DATA_FILE = "user_data.json"
LINKS_FILE = "user_links.json"
COUNTER_FILE = "counter.json"
PAYOUT_FILE = "payout_counter.json"
TON_ADDRESSES_FILE = "ton_addresses.json"
HISTORY_FILE = "history.json"
APPROVED_FILE = "approved_users.json"

user_questions = {}
user_answers = {}
application_counter = 0
payout_counter = 0
user_data = {}
user_links = {}
user_ton_addresses = {}
user_history = {}
user_payout_messages = {}
approved_users = set()

def load_data():
    global application_counter, user_data, user_links, payout_counter, user_ton_addresses, user_history, approved_users
    
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            application_counter = data.get('counter', 0)
    
    if os.path.exists(PAYOUT_FILE):
        with open(PAYOUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            payout_counter = data.get('counter', 0)
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
            for user_id in user_data:
                if 'join_date' in user_data[user_id]:
                    user_data[user_id]['join_date'] = datetime.fromisoformat(user_data[user_id]['join_date'])
    
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            user_links = json.load(f)
    
    if os.path.exists(TON_ADDRESSES_FILE):
        with open(TON_ADDRESSES_FILE, 'r', encoding='utf-8') as f:
            user_ton_addresses = json.load(f)
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            user_history = json.load(f)
    
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, 'r', encoding='utf-8') as f:
            approved_users = set(json.load(f))

def save_data():
    with open(COUNTER_FILE, 'w', encoding='utf-8') as f:
        json.dump({'counter': application_counter}, f, ensure_ascii=False, indent=2)
    
    with open(PAYOUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({'counter': payout_counter}, f, ensure_ascii=False, indent=2)
    
    data_to_save = {}
    for user_id, data in user_data.items():
        data_to_save[user_id] = data.copy()
        if 'join_date' in data_to_save[user_id]:
            data_to_save[user_id]['join_date'] = data_to_save[user_id]['join_date'].isoformat()
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    
    with open(LINKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_links, f, ensure_ascii=False, indent=2)
    
    with open(TON_ADDRESSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_ton_addresses, f, ensure_ascii=False, indent=2)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_history, f, ensure_ascii=False, indent=2)
    
    with open(APPROVED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(approved_users), f, ensure_ascii=False, indent=2)

load_data()

async def send_welcome_with_menu(chat_id: int, text: str):
    """Отправляет приветственное изображение с меню, если файл существует"""
    try:
        # Проверяем, существует ли файл welcome.png
        if os.path.exists("welcome.png"):
            welcome_image = FSInputFile("welcome.png")
            await bot.send_photo(
                chat_id,
                photo=welcome_image,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # Если файл не найден, отправляем просто текст
            logging.warning("welcome.png не найден, отправляем текстовое сообщение")
            await bot.send_message(chat_id, text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Ошибка при отправке welcome.png: {e}")
        # В случае ошибки отправляем текстовое сообщение
        await bot.send_message(chat_id, text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.HTML)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    
    # Проверяем, одобрен ли пользователь
    if user_id in approved_users:
        text = (f'<tg-emoji emoji-id="5938537205847822613">👋</tg-emoji> <b>Добро пожаловать в MMM Team.</b>\n\nЗдесь вы сможете подать заявку на выплату или стать траффером тимы.')
        await send_welcome_with_menu(message.chat.id, text)
        return
    
    try:
        member = await bot.get_chat_member(GROUP_ID, message.from_user.id)
        if member.status in ['member', 'administrator', 'creator']:
            if user_id not in user_data:
                user_data[user_id] = {
                    "join_date": datetime.now(),
                    "profits": 0,
                    "sum_profits": 0,
                    "invites": 0,
                    "leaves": 0,
                    "invited_by": None
                }
                save_data()
            text = (f'<tg-emoji emoji-id="5938537205847822613">👋</tg-emoji> <b>Добро пожаловать в MMM Team.</b>\n\nЗдесь вы сможете подать заявку на выплату или стать траффером тимы.')
            await send_welcome_with_menu(message.chat.id, text)
            return
    except:
        pass
    
    text = (f'<tg-emoji emoji-id="5927118708873892465">👋</tg-emoji> <b>Добро пожаловать в панель тимы MMM.</b>\n\nДля принятия заявки в тиму, я попрошу тебя ответить на пару вопросов.')
    await message.answer(text, reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)

@dp.message(Command("giveprofit"))
async def give_profits(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для этой команды.")
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Использование: /giveprofit <user_id> <количество>")
        return
    
    try:
        user_id = str(args[1])
        amount = int(args[2])
        
        if user_id not in user_data:
            await message.answer("Пользователь не найден в базе данных.")
            return
        
        user_data[user_id]["profits"] = user_data[user_id].get("profits", 0) + amount
        save_data()
        await message.answer(f"✅ Пользователю {user_id} начислено {amount} профитов. Всего: {user_data[user_id]['profits']}")
    except ValueError:
        await message.answer("Неверный формат ID или количества.")

@dp.message(Command("summaprofit"))
async def give_sum_profits(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для этой команды.")
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Использование: /summaprofit <user_id> <количество>")
        return
    
    try:
        user_id = str(args[1])
        amount = int(args[2])
        
        if user_id not in user_data:
            await message.answer("Пользователь не найден в базе данных.")
            return
        
        user_data[user_id]["sum_profits"] = user_data[user_id].get("sum_profits", 0) + amount
        save_data()
        await message.answer(f"✅ Пользователю {user_id} начислено {amount} суммы профитов. Всего: {user_data[user_id]['sum_profits']}")
    except ValueError:
        await message.answer("Неверный формат ID или количества.")

@dp.chat_member()
async def handle_chat_member(event: ChatMemberUpdated):
    chat_id = event.chat.id
    
    if chat_id != GROUP_ID:
        return
    
    user_id = str(event.from_user.id)
    
    if event.new_chat_member.status in ['member', 'administrator', 'creator']:
        if event.invite_link:
            invite_link = event.invite_link.invite_link
            
            for owner_id, link_data in user_links.items():
                if link_data.get("link") == invite_link:
                    if owner_id in user_data:
                        user_data[owner_id]["invites"] = user_data[owner_id].get("invites", 0) + 1
                    else:
                        user_data[owner_id] = {
                            "join_date": datetime.now(),
                            "profits": 0,
                            "sum_profits": 0,
                            "invites": 1,
                            "leaves": 0,
                            "invited_by": None
                        }
                    
                    if user_id not in user_data:
                        user_data[user_id] = {
                            "join_date": datetime.now(),
                            "profits": 0,
                            "sum_profits": 0,
                            "invites": 0,
                            "leaves": 0,
                            "invited_by": owner_id
                        }
                    else:
                        user_data[user_id]["invited_by"] = owner_id
                    
                    save_data()
                    logging.info(f"User {user_id} joined via link from {owner_id}")
                    break
        
        if user_id not in user_data:
            user_data[user_id] = {
                "join_date": datetime.now(),
                "profits": 0,
                "sum_profits": 0,
                "invites": 0,
                "leaves": 0,
                "invited_by": None
            }
            save_data()
    
    elif event.old_chat_member.status in ['member', 'administrator', 'creator'] and event.new_chat_member.status == 'left':
        if user_id in user_data:
            user_data[user_id]["leaves"] = user_data[user_id].get("leaves", 0) + 1
        
        if user_id in user_data and "invited_by" in user_data[user_id]:
            inviter_id = user_data[user_id]["invited_by"]
            if inviter_id in user_data:
                user_data[inviter_id]["leaves"] = user_data[inviter_id].get("leaves", 0) + 1
        
        save_data()
        logging.info(f"User {user_id} left the group")

@dp.callback_query(lambda c: c.data and c.data.startswith("success") and not c.data.startswith("success_accept") and not c.data.startswith("success_payout"))
async def process_success(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    user_id = str(callback.from_user.id)
    
    # Проверяем, не одобрен ли уже пользователь
    if user_id in approved_users:
        text = (f'<tg-emoji emoji-id="5938537205847822613">👋</tg-emoji> <b>Вы уже в команде!</b>')
        await send_welcome_with_menu(callback.message.chat.id, text)
        return
    
    user_questions[user_id] = 1
    user_answers[user_id] = {}
    text = (f'<tg-emoji emoji-id="5794182096603847292">❓</tg-emoji> <b>Вопрос 1.</b>\n\nСколько времени ты готов уделять нашей команде?')
    await callback.message.answer(text, parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data and c.data.startswith("danger") and not c.data.startswith("danger_decline") and not c.data.startswith("danger_payout"))
async def process_danger(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()

@dp.message(lambda message: (message.photo or message.document) and str(message.from_user.id) in user_questions and user_questions[str(message.from_user.id)] == 'payout_screenshots')
async def handle_payout_screenshot(message: Message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_answers:
        user_answers[user_id] = {}
    
    if 'screenshots' not in user_answers[user_id]:
        user_answers[user_id]['screenshots'] = []
    
    if len(user_answers[user_id].get('screenshots', [])) >= 10:
        await message.answer("❌ Вы уже загрузили максимальное количество скринов (10). Нажмите 'Далее' для продолжения.")
        await message.delete()
        return
    
    if message.photo:
        file_id = message.photo[-1].file_id
        user_answers[user_id]['screenshots'].append(file_id)
    elif message.document:
        file_id = message.document.file_id
        user_answers[user_id]['screenshots'].append(file_id)
    
    await message.delete()
    
    count = len(user_answers[user_id]['screenshots'])
    text = (f'<tg-emoji emoji-id="5924498929147189381">📸</tg-emoji> <b>Отправьте скрины передачи подарков от лица мамонта</b>\n\n(Принимаются только скрины, текстовые сообщения будут удалены)\n\n<b>Скринов загружено: {count}/10</b>')
    
    try:
        if user_id in user_payout_messages:
            await bot.edit_message_text(
                text,
                chat_id=message.chat.id,
                message_id=user_payout_messages[user_id],
                reply_markup=get_payout_screenshot_keyboard(),
                parse_mode=ParseMode.HTML
            )
        else:
            msg = await message.answer(text, reply_markup=get_payout_screenshot_keyboard(), parse_mode=ParseMode.HTML)
            user_payout_messages[user_id] = msg.message_id
    except Exception as e:
        logging.error(f"Error editing message: {e}")
        msg = await message.answer(text, reply_markup=get_payout_screenshot_keyboard(), parse_mode=ParseMode.HTML)
        user_payout_messages[user_id] = msg.message_id

@dp.message(lambda message: message.text and str(message.from_user.id) in user_questions and user_questions[str(message.from_user.id)] == 'payout_screenshots')
async def handle_payout_text_delete(message: Message):
    await message.delete()

@dp.message(lambda message: message.text and str(message.from_user.id) in user_questions and user_questions[str(message.from_user.id)] == 'payout_ton')
async def handle_payout_ton(message: Message):
    user_id = str(message.from_user.id)
    
    if message.text and not message.text.startswith('/'):
        user_answers[user_id]['ton_address'] = message.text
        await send_payout_to_admin(message.from_user)
        del user_questions[user_id]
        text = (f'<tg-emoji emoji-id="6042098561095570207">✅</tg-emoji> <b>Заявка успешно улетела на проверку.</b>')
        await message.answer(text, reply_markup=get_payout_keyboard(), parse_mode=ParseMode.HTML)

@dp.message()
async def handle_answers(message: Message):
    user_id = str(message.from_user.id)
    
    # Если пользователь не в процессе заполнения заявки - игнорируем
    if user_id not in user_questions:
        return
    
    # Если это команда - игнорируем
    if message.text and message.text.startswith('/'):
        return
    
    # Обработка TON адреса
    if user_questions[user_id] == 'ton_name':
        user_answers[user_id]['ton_name'] = message.text
        user_questions[user_id] = 'ton_address_input'
        text = (f'<tg-emoji emoji-id="6041720006973067267">💳</tg-emoji> <b>Введите адрес</b>')
        await message.answer(text, parse_mode=ParseMode.HTML)
        return
    
    if user_questions[user_id] == 'ton_address_input':
        if user_id not in user_ton_addresses:
            user_ton_addresses[user_id] = {}
        name = user_answers[user_id].get('ton_name', 'Без названия')
        user_ton_addresses[user_id][name] = message.text
        save_data()
        del user_questions[user_id]
        text = (f'<tg-emoji emoji-id="6041720006973067267">✅</tg-emoji> <b>Адрес "{name}" сохранен!</b>')
        await message.answer(text, reply_markup=get_profile_keyboard(), parse_mode=ParseMode.HTML)
        return
    
    # Обработка заявки на выплату
    if user_questions[user_id] in ['payout_deal', 'payout_links']:
        await handle_payout_answers(message)
        return
    
    # Обработка вопросов для вступления
    if user_questions[user_id] == 1:
        user_answers[user_id]['time'] = message.text
        user_questions[user_id] = 2
        text = (f'<tg-emoji emoji-id="5794085322400733645">❓</tg-emoji> <b>Вопрос 2.</b>\n\nСколько у тебя опыта в сфере NFT подарков?')
        await message.answer(text, parse_mode=ParseMode.HTML)
    
    elif user_questions[user_id] == 2:
        user_answers[user_id]['experience'] = message.text
        user_questions[user_id] = 3
        text = (f'<tg-emoji emoji-id="5794280000383358988">❓</tg-emoji> <b>Вопрос 3.</b>\n\nНа сколько хорошо ты понимаешь систему ворка?')
        await message.answer(text, reply_markup=get_question3_keyboard(), parse_mode=ParseMode.HTML)
        await message.delete()

async def handle_payout_answers(message: Message):
    user_id = str(message.from_user.id)
    
    if user_questions[user_id] == 'payout_deal':
        user_answers[user_id]['deal_number'] = message.text
        user_questions[user_id] = 'payout_links'
        text = (f'<tg-emoji emoji-id="5924498929147189381">📎</tg-emoji> <b>Введите ссылки на подарки</b>')
        await message.answer(text, parse_mode=ParseMode.HTML)
    
    elif user_questions[user_id] == 'payout_links':
        user_answers[user_id]['gift_links'] = message.text
        user_questions[user_id] = 'payout_screenshots'
        user_answers[user_id]['screenshots'] = []
        
        text = (f'<tg-emoji emoji-id="5924498929147189381">📸</tg-emoji> <b>Отправьте скрины передачи подарков от лица мамонта</b>\n\n(Принимаются только скрины, текстовые сообщения будут удалены)\n\n<b>Скринов загружено: 0/10</b>')
        msg = await message.answer(text, reply_markup=get_payout_screenshot_keyboard(), parse_mode=ParseMode.HTML)
        user_payout_messages[user_id] = msg.message_id

@dp.callback_query(lambda c: c.data and c.data.startswith("payout_next"))
async def handle_payout_next(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    
    if user_id not in user_answers or len(user_answers[user_id].get('screenshots', [])) == 0:
        await callback.message.answer("❌ Вы должны загрузить хотя бы один скрин.")
        return
    
    user_questions[user_id] = 'payout_ton'
    text = (f'<tg-emoji emoji-id="5924498929147189381">💳</tg-emoji> <b>Введите ваш адрес TON сети</b>\n\n(Он будет сохранен для будущих выплат)')
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    
    try:
        await callback.message.delete()
    except:
        pass

async def send_payout_to_admin(user):
    global payout_counter
    payout_counter += 1
    payout_number = str(payout_counter).zfill(3)
    save_data()
    
    user_info = await bot.get_chat(user.id)
    username = user_info.username or "Нет username"
    user_id = str(user.id)
    
    answers = user_answers.get(user_id, {})
    
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append({
        "type": "payout",
        "number": payout_number,
        "status": "pending",
        "date": datetime.now().isoformat()
    })
    save_data()
    
    text = (
        f'<tg-emoji emoji-id="6042098561095570207">💳</tg-emoji> <b>Заявка на выплату #{payout_number}</b>\n\n'
        f'<tg-emoji emoji-id="6039486778597970865">👤</tg-emoji> <b>Отправитель:</b> @{username} (id: {user.id})\n'
        f'<tg-emoji emoji-id="5924498929147189381">🔢</tg-emoji> <b>Сделка:</b> {answers.get("deal_number", "Не указано")}\n'
        f'<tg-emoji emoji-id="5924498929147189381">🔗</tg-emoji> <b>Ссылки на NFT:</b> {answers.get("gift_links", "Не указано")}\n'
        f'<tg-emoji emoji-id="5924498929147189381">💳</tg-emoji> <b>Адрес для выплаты:</b> {answers.get("ton_address", "Не указано")}\n'
        f'<tg-emoji emoji-id="5924498929147189381">📸</tg-emoji> <b>Скрины:</b> ниже'
    )
    
    # Отправляем админу с обработкой ошибок
    try:
        await bot.send_message(
            ADMIN_ID,
            text,
            reply_markup=get_payout_admin_keyboard(user.id, payout_number),
            parse_mode=ParseMode.HTML
        )
        
        if 'screenshots' in answers:
            for file_id in answers['screenshots']:
                try:
                    await bot.send_document(ADMIN_ID, file_id)
                except:
                    try:
                        await bot.send_photo(ADMIN_ID, file_id)
                    except:
                        pass
    except Exception as e:
        logging.error(f"Не удалось отправить заявку на выплату #{payout_number} админу: {e}")

@dp.callback_query(lambda c: c.data and c.data.startswith("success_payout"))
async def handle_payout_accept(callback: CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split("_")
    user_id = str(parts[2])
    payout_number = parts[3]
    
    await callback.message.delete()
    
    if user_id in user_history:
        for item in user_history[user_id]:
            if item.get("number") == payout_number and item.get("type") == "payout":
                item["status"] = "approved"
                save_data()
                break
    
    text = (
        f'<tg-emoji emoji-id="6041720006973067267">✅</tg-emoji> <b>Заявка #{payout_number} выплачена</b>'
    )
    await bot.send_message(int(user_id), text, parse_mode=ParseMode.HTML)
    
    if user_id in user_answers:
        del user_answers[user_id]
    
    await callback.message.answer("✅ Заявка выплачена!")

@dp.callback_query(lambda c: c.data and c.data.startswith("danger_payout"))
async def handle_payout_decline(callback: CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split("_")
    user_id = str(parts[2])
    payout_number = parts[3]
    
    await callback.message.delete()
    
    if user_id in user_history:
        for item in user_history[user_id]:
            if item.get("number") == payout_number and item.get("type") == "payout":
                item["status"] = "declined"
                save_data()
                break
    
    text = (
        f'<tg-emoji emoji-id="6041716699848249286">❌</tg-emoji> <b>Заявка #{payout_number} отклонена</b>'
    )
    await bot.send_message(int(user_id), text, parse_mode=ParseMode.HTML)
    
    if user_id in user_answers:
        del user_answers[user_id]
    
    await callback.message.answer("❌ Заявка отклонена!")

@dp.callback_query(lambda c: c.data and c.data.startswith("q3"))
async def handle_question3(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    if user_id not in user_questions:
        await callback.message.answer("Пожалуйста, начните сначала с команды /start")
        return
    
    if user_questions[user_id] != 3:
        return
    
    if callback.data == "q3_normal":
        user_answers[user_id]['understanding'] = "Есть непонятные темы."
    elif callback.data == "q3_success":
        user_answers[user_id]['understanding'] = "Мне всё понятно."
    else:
        return
    
    del user_questions[user_id]
    await callback.message.delete()
    
    await send_application_to_admin(callback.from_user)
    
    final_text = (f'<tg-emoji emoji-id="5823268688874179761">✅</tg-emoji> <b>Твоя поданная заявка была отправлена на рассмотрение.</b>')
    await callback.message.answer(final_text, reply_markup=get_final_keyboard(), parse_mode=ParseMode.HTML)

async def send_application_to_admin(user):
    global application_counter
    application_counter += 1
    app_number = str(application_counter).zfill(3)
    save_data()
    
    user_info = await bot.get_chat(user.id)
    username = user_info.username or "Нет username"
    user_id = str(user.id)
    
    answers = user_answers.get(user_id, {})
    
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append({
        "type": "application",
        "number": app_number,
        "status": "pending",
        "date": datetime.now().isoformat()
    })
    save_data()
    
    text = (
        f'<tg-emoji emoji-id="5940433880585605708">📝</tg-emoji> <b>Заявка #{app_number}</b>\n\n'
        f'<tg-emoji emoji-id="6039486778597970865">👤</tg-emoji> Отправил: @{username} (id: {user.id})\n'
        f'<tg-emoji emoji-id="5890925363067886150">⏰</tg-emoji> Готов уделять времени: {answers.get("time", "Не указано")}\n'
        f'<tg-emoji emoji-id="5890925363067886150">💼</tg-emoji> Опыт в сфере: {answers.get("experience", "Не указано")}\n'
        f'<tg-emoji emoji-id="5890925363067886150">📖</tg-emoji> Насколько понятен смысл ворка: {answers.get("understanding", "Не указано")}'
    )
    
    # Отправляем админу с обработкой ошибок
    try:
        await bot.send_message(
            ADMIN_ID,
            text,
            reply_markup=get_admin_keyboard(user.id, app_number),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Не удалось отправить заявку #{app_number} админу: {e}")

@dp.callback_query(lambda c: c.data and c.data.startswith("success_accept"))
async def handle_accept(callback: CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split("_")
    user_id = str(parts[2])
    app_number = parts[3]
    
    await callback.message.delete()
    
    # Добавляем пользователя в список одобренных
    approved_users.add(user_id)
    save_data()
    
    if user_id in user_history:
        for item in user_history[user_id]:
            if item.get("number") == app_number and item.get("type") == "application":
                item["status"] = "approved"
                save_data()
                break
    
    if user_id not in user_data:
        user_data[user_id] = {
            "join_date": datetime.now(),
            "profits": 0,
            "sum_profits": 0,
            "invites": 0,
            "leaves": 0,
            "invited_by": None
        }
        save_data()
    
    # Отправляем приветственное изображение
    try:
        if os.path.exists("welcome.png"):
            welcome_image = FSInputFile("welcome.png")
            await bot.send_photo(
                int(user_id),
                photo=welcome_image,
                caption=f'<tg-emoji emoji-id="6030445631921721471">✅</tg-emoji> <b>Заявка #{app_number} одобрена.</b>\n\nНаша команда: https://t.me/+NGKWxK04XeVmMDgx',
                parse_mode=ParseMode.HTML,
                reply_markup=get_accepted_keyboard()
            )
        else:
            # Если файл не найден, отправляем обычное сообщение
            logging.warning("welcome.png не найден, отправляем текстовое сообщение")
            text = (
                f'<tg-emoji emoji-id="6030445631921721471">✅</tg-emoji> <b>Заявка #{app_number} одобрена.</b>\n\n'
                f'Наша команда: https://t.me/+NGKWxK04XeVmMDgx'
            )
            await bot.send_message(int(user_id), text, reply_markup=get_accepted_keyboard(), parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Ошибка при отправке welcome.png: {e}")
        # В случае ошибки отправляем текстовое сообщение
        text = (
            f'<tg-emoji emoji-id="6030445631921721471">✅</tg-emoji> <b>Заявка #{app_number} одобрена.</b>\n\n'
            f'Наша команда: https://t.me/+NGKWxK04XeVmMDgx'
        )
        await bot.send_message(int(user_id), text, reply_markup=get_accepted_keyboard(), parse_mode=ParseMode.HTML)
    
    if user_id in user_answers:
        del user_answers[user_id]
    
    await callback.message.answer("✅ Заявка одобрена!")

@dp.callback_query(lambda c: c.data and c.data.startswith("danger_decline"))
async def handle_decline(callback: CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split("_")
    user_id = str(parts[2])
    app_number = parts[3]
    
    await callback.message.delete()
    
    if user_id in user_history:
        for item in user_history[user_id]:
            if item.get("number") == app_number and item.get("type") == "application":
                item["status"] = "declined"
                save_data()
                break
    
    text = (
        f'<tg-emoji emoji-id="6041716699848249286">❌</tg-emoji> <b>Ваша заявка #{app_number} была отклонена.</b>'
    )
    await bot.send_message(int(user_id), text, parse_mode=ParseMode.HTML)
    
    if user_id in user_answers:
        del user_answers[user_id]
    
    await callback.message.answer("❌ Заявка отклонена.")

@dp.callback_query(lambda c: c.data and c.data.startswith("check_status"))
async def handle_check_status(callback: CallbackQuery):
    await callback.answer("На проверке...", show_alert=True)

@dp.callback_query(lambda c: c.data and c.data.startswith("main_menu"))
async def handle_main_menu(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    
    # Проверяем, одобрен ли пользователь
    if user_id not in approved_users:
        # Если не одобрен, отправляем анкету
        text = (f'<tg-emoji emoji-id="5927118708873892465">👋</tg-emoji> <b>Добро пожаловать в панель тимы MMM.</b>\n\nДля принятия заявки в тиму, я попрошу тебя ответить на пару вопросов.')
        await callback.message.answer(text, reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
        return
    
    text = (f'<tg-emoji emoji-id="5938537205847822613">👋</tg-emoji> <b>Добро пожаловать в MMM Team.</b>\n\nЗдесь вы сможете подать заявку на выплату или стать траффером тимы.')
    await send_welcome_with_menu(callback.message.chat.id, text)

@dp.callback_query(lambda c: c.data and c.data.startswith("profile"))
async def handle_profile(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    data = user_data.get(user_id, {
        "join_date": datetime.now(),
        "profits": 0,
        "sum_profits": 0,
        "invites": 0,
        "leaves": 0
    })
    
    if isinstance(data["join_date"], str):
        join_date = datetime.fromisoformat(data["join_date"])
    else:
        join_date = data["join_date"]
    days_in_team = (datetime.now() - join_date).days
    
    text = (
        f'<tg-emoji emoji-id="6032994772321309200">👤</tg-emoji> <b>Ваш профиль:</b>\n\n'
        f'<b>Количество дней в команде:</b> {days_in_team}\n'
        f'<tg-emoji emoji-id="5258204546391351475">💰</tg-emoji> <b>Количество профитов:</b> {data.get("profits", 0)}\n'
        f'<tg-emoji emoji-id="5258204546391351475">💰</tg-emoji> <b>Сумма профитов:</b> {data.get("sum_profits", 0)}'
    )
    
    await callback.message.answer(text, reply_markup=get_profile_keyboard(), parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data and c.data.startswith("ton_address"))
async def handle_ton_address(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    addresses = user_ton_addresses.get(user_id, {})
    
    if addresses:
        text = (f'<tg-emoji emoji-id="6042069608721027027">💳</tg-emoji> <b>Ваши TON адреса:</b>\n\n')
        for name, addr in addresses.items():
            text += f'<b>• {name}:</b>\n<code>{addr}</code>\n\n'
        await callback.message.answer(text, reply_markup=get_ton_address_list_keyboard(), parse_mode=ParseMode.HTML)
    else:
        user_questions[user_id] = 'ton_name'
        if user_id not in user_answers:
            user_answers[user_id] = {}
        text = (f'<tg-emoji emoji-id="6041720006973067267">💳</tg-emoji> <b>Введите название для адреса</b>')
        await callback.message.answer(text, parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data and c.data.startswith("ton_add"))
async def handle_ton_add(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    user_questions[user_id] = 'ton_name'
    if user_id not in user_answers:
        user_answers[user_id] = {}
    text = (f'<tg-emoji emoji-id="6041720006973067267">💳</tg-emoji> <b>Введите название для адреса</b>')
    await callback.message.answer(text, parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data and c.data.startswith("ton_back"))
async def handle_ton_back(callback: CallbackQuery):
    await callback.answer()
    await handle_profile(callback)

@dp.callback_query(lambda c: c.data and c.data.startswith("history"))
async def handle_history(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    history = user_history.get(user_id, [])
    
    if not history:
        text = (f'<tg-emoji emoji-id="5850317551090800862">📋</tg-emoji> <b>История заявок пуста.</b>')
        await callback.message.answer(text, reply_markup=get_profile_keyboard(), parse_mode=ParseMode.HTML)
        return
    
    text = (f'<tg-emoji emoji-id="5850317551090800862">📋</tg-emoji> <b>История заявок:</b>\n\n')
    
    for item in reversed(history[-10:]):
        status_emoji = {
            "pending": "⏳",
            "approved": "✅",
            "declined": "❌"
        }.get(item.get("status"), "❓")
        
        status_text = {
            "pending": "Подана",
            "approved": "Принята",
            "declined": "Отказана"
        }.get(item.get("status"), "Неизвестно")
        
        type_text = "Выплата" if item.get("type") == "payout" else "Заявка"
        
        text += f'<tg-emoji emoji-id="6041720006973067267">📌</tg-emoji> <b>#{item.get("number")}</b> - {type_text} - {status_emoji} {status_text}\n'
    
    await callback.message.answer(text, reply_markup=get_profile_keyboard(), parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data and c.data.startswith("payout"))
async def handle_payout_start(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    
    # Проверяем, одобрен ли пользователь
    if user_id not in approved_users:
        await callback.message.answer("❌ Сначала подайте заявку на вступление в команду через /start")
        return
    
    if user_id not in user_data:
        await callback.message.answer("❌ Сначала подайте заявку на вступление в команду через /start")
        return
    
    user_questions[user_id] = 'payout_deal'
    if user_id not in user_answers:
        user_answers[user_id] = {}
    
    text = (f'<tg-emoji emoji-id="5924498929147189381">💳</tg-emoji> <b>Подача заявки.</b>\n\nВведите номер сделки через #')
    await callback.message.answer(text, parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data and c.data.startswith("traffic"))
async def handle_traffic(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    
    # Проверяем, одобрен ли пользователь
    if user_id not in approved_users:
        await callback.message.answer("❌ Сначала подайте заявку на вступление в команду через /start")
        return
    
    data = user_data.get(user_id, {
        "invites": 0,
        "leaves": 0
    })
    link_data = user_links.get(user_id, {})
    
    if link_data and "link" in link_data:
        text = (
            f'<tg-emoji emoji-id="6028435952299413210">📊</tg-emoji> <b>Статус:</b> Ссылка активна\n\n'
            f'<b>Количество приглашённых:</b> {data.get("invites", 0)}\n'
            f'<b>Количество покинувших группу:</b> {data.get("leaves", 0)}\n\n'
            f'<b>Ваша ссылка:</b> {link_data["link"]}'
        )
        await callback.message.answer(text, reply_markup=get_traffic_link_keyboard(), parse_mode=ParseMode.HTML)
    else:
        text = (
            f'<tg-emoji emoji-id="6028435952299413210">📊</tg-emoji> <b>Статус:</b> Нету личной ссылки\n\n'
            f'<b>Количество приглашённых:</b> {data.get("invites", 0)}\n'
            f'<b>Количество покинувших группу:</b> {data.get("leaves", 0)}'
        )
        await callback.message.answer(text, reply_markup=get_traffic_keyboard(), parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data and c.data.startswith("get_link"))
async def handle_get_link(callback: CallbackQuery):
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    
    # Проверяем, одобрен ли пользователь
    if user_id not in approved_users:
        await callback.message.answer("❌ Сначала подайте заявку на вступление в команду через /start")
        return
    
    try:
        invite_link = await bot.create_chat_invite_link(
            chat_id=GROUP_ID,
            name=f"User_{user_id}",
            creates_join_request=True
        )
        
        user_links[user_id] = {
            "link": invite_link.invite_link,
            "invites": 0,
            "leaves": 0
        }
        save_data()
        
        text = (
            f'<tg-emoji emoji-id="6028171274939797252">🔗</tg-emoji> <b>Ссылка создана!</b>\n\n'
            f'{invite_link.invite_link}\n\n'
            f'<b>Статус:</b> Ссылка создана с заявкой на вступление'
        )
        await callback.message.answer(text, reply_markup=get_traffic_link_keyboard(), parse_mode=ParseMode.HTML)
    except Exception as e:
        await callback.message.answer(f"Ошибка при создании ссылки: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
