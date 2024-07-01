from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder
from keyboards import *
from media import *
from asyncio import sleep
from config import config_1
from psycopg2 import connect
from psycopg2.errors import UniqueViolation
from asyncio import new_event_loop, set_event_loop
from os import system
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


dp = Dispatcher()
bot = Bot(token=config_1.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

class Form(StatesGroup):
    await_msg_name = State()
    await_msg_number = State()
    await_msg_email = State()
    wait_lesson = State()

class Admin(StatesGroup):
    await_msg = State()

class Feedback(StatesGroup):
    feedback = State()

@dp.message(F.photo)
async def photo_handler(message: Message) -> None:
    photo_data = message.photo[-1]

    await message.answer(f'{photo_data}')

# @dp.message(F.video)
# async def photo_handler(message: Message) -> None:
#     photo_data = message.video

#     await message.answer(f'{photo_data}')

# @dp.message(F.document)
# async def photo_handler(message: Message) -> None:
#     photo_data = message.document

#     await message.answer(f'{photo_data}')

# @dp.message(F.voice)
# async def photo_handler(message: Message) -> None:
#     photo_data = message.voice.file_id

#     await message.answer(f'{photo_data}')


admins = ["1051818216", "6189886745", "144398908"]

@dp.callback_query(F.data == "Хотите попробовать функции юзера?") 
async def send_random_value(callback: CallbackQuery, state: FSMContext):
    await user_start(callback.message, state)

@dp.callback_query(F.data == "Настроить рассылку")
async def get_message(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    await state.set_state(Admin.await_msg)
    await callback.message.answer("Введите текст, который вы хотите разослать или добавьте медиа-файлы")

@dp.message(Admin.await_msg)
async def send_msg(message: Message, state: FSMContext) -> None:
    await state.update_data(await_msg = message)

    sure = await message.answer(text = "Вы уверены, что хотите отправить это сообщение?", 
                                reply_markup = are_you_sure())
    await state.update_data(delete_msg = sure.message_id)

@dp.callback_query(F.data == "Да")
async def send_all(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("")

    data = await state.get_data()
    mes = data.get("await_msg")
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT tg_id FROM "person"''')
        our_users = cursor.fetchall()
    except Exception as e:
        print(f"The error '{e}' occurred")
    
    if mes.photo == None:
        for user in our_users:
            try:
                await bot.send_message(chat_id=user[0], text=mes.text)
            except:
                continue
    else:
        for user in our_users:
            await bot.send_photo(chat_id=user[0], photo=mes.photo[-1].file_id, caption=mes.caption)

    await callback.message.answer("Сообщение отправлено пользователям", reply_markup=admin_kb())
    await state.clear()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id = data.get("delete_msg"))

@dp.callback_query(F.data == "Нет")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    data = await state.get_data()
    await callback.message.answer("Сообщение не отправлено", reply_markup=admin_kb())
    await state.clear()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id = data.get("delete_msg"))

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    
    await create_user(message.from_user.username, message.from_user.first_name, message.from_user.last_name, tg_id=message.from_user.id)
    
    if str(message.from_user.id) in admins:
        await message.answer("Если захотите вернуться к этому меню, то нажмите /start",
                             reply_markup=admin_kb())

    else:
        await user_start(message, state)
    

async def user_start(message, state):

    await state.set_state(Form.wait_lesson)
    await message.answer_photo(photo=first_photo, caption=first_text, reply_markup=main_reply_kb)
    await message.answer_document(document=checklist_file, caption=like_text, reply_markup=give_start_kb())
    await sleep(5*60)
    if await state.get_state() == "Form:wait_lesson":
        await message.answer_video(video=lesson_video, caption=lesson_text, reply_markup=reaction_kb())
    await sleep(15*60)
    if await state.get_state() == "Form:wait_lesson":
        await message.answer(text=second_ping_text)
    await sleep(3*60*60)
    if await state.get_state() == "Form:wait_lesson":
        await message.answer(text=product_text, reply_markup=product_kb())


async def create_user(username, first_name, last_name, tg_id):
    try:
        connection = connect(config_1.POSTGRES_URL)
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO "person" (username, first_name, last_name, tg_id) VALUES ('{username}', '{first_name}', '{last_name}', '{tg_id}')''')
        connection.commit()
        connection.close()
    except UniqueViolation:
        pass

@dp.callback_query(F.data == "Обо мне")
async def get_message_about(callback: CallbackQuery):
    media = MediaGroupBuilder(caption=about1_text)
    media.add_photo(media=about_photo1)
    media.add_photo(media=about_photo2)
    media.add_photo(media=about_photo3)
    media.add_photo(media=about_photo4)
    media.add_photo(media=about_photo5)
    await callback.message.answer_media_group(media=media.build())
    await callback.message.answer(text=about2_text, reply_markup=personal_work_kb())

@dp.callback_query(F.data == "Получить урок")
async def get_lesson(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer_video(video=lesson_video, caption=lesson_text, reply_markup=reaction_kb())
    await state.clear()

@dp.callback_query(F.data == "лайк")
async def get_message_like(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=product_text, reply_markup=product_kb())
    await state.clear()

@dp.callback_query(F.data == "дизлайк")
async def get_message_dis(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=dislike_text)
    await state.clear()

@dp.callback_query(F.data == "Интенсив")
async def get_message_intensive(callback: CallbackQuery):
    media = MediaGroupBuilder(caption=plan_intensive_text1)
    media.add_photo(media=plan_intensive_photo1)
    media.add_photo(media=plan_intensive_photo2)
    media.add_photo(media=plan_intensive_photo3)
    media.add_photo(media=plan_intensive_photo4)
    media.add_photo(media=plan_intensive_photo5)
    media.add_photo(media=plan_intensive_photo6)
    media.add_photo(media=plan_intensive_photo7)
    media.add_photo(media=plan_intensive_photo8)
    media.add_photo(media=plan_intensive_photo9)
    await callback.message.answer_media_group(media=media.build())
    await callback.message.answer(text=plan_intensive_text2, reply_markup=give_prodamus_link(callback.from_user.id))

@dp.message(F.text == "Интенсив")
async def get_message_intensive1(message: Message):    
    media = MediaGroupBuilder(caption=plan_intensive_text1)
    media.add_photo(media=plan_intensive_photo1)
    media.add_photo(media=plan_intensive_photo2)
    media.add_photo(media=plan_intensive_photo3)
    media.add_photo(media=plan_intensive_photo4)
    media.add_photo(media=plan_intensive_photo5)
    media.add_photo(media=plan_intensive_photo6)
    media.add_photo(media=plan_intensive_photo7)
    media.add_photo(media=plan_intensive_photo8)
    media.add_photo(media=plan_intensive_photo9)
    await message.answer_media_group(media=media.build())
    await message.answer(text=plan_intensive_text2, reply_markup=give_prodamus_link(message.from_user.id))

@dp.callback_query(F.data == "Женский клуб")
async def get_message_club(callback: CallbackQuery):
    await callback.message.answer(text=club_text, reply_markup=club_kb())

@dp.message(F.text == "Женский клуб")
async def get_message_club(message: Message):
    await message.answer(text=club_text, reply_markup=club_kb())

@dp.callback_query(F.data == "Личная работа")
async def get_message_personal(callback: CallbackQuery):
    await callback.message.answer(text=personal_work_text, reply_markup=personal_work_kb())

@dp.message(F.text == "Личная работа")
async def get_message_personal(message: Message):
    await message.answer(text=personal_work_text, reply_markup=personal_work_kb())

@dp.callback_query(F.data == "Узнать подробнее")
async def get_message(callback: CallbackQuery):
    await callback.message.answer(text=podrobnee_text)

@dp.callback_query(F.data == "Записаться на презентацию")
async def get_message(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.await_msg_name)
    await state.update_data(type = "Запись на презентацию клуба")
    await callback.message.answer(text=needhelp1_text)

@dp.callback_query(F.data == "Личные")
async def get_message(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.await_msg_name)
    await state.update_data(type = "Личное посещение")
    await callback.message.answer(text=needhelp1_text)

@dp.message(Form.await_msg_name, F.text)
async def get_message(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    await state.set_state(Form.await_msg_number)
    await message.answer(text=needhelp2_text)

@dp.message(Form.await_msg_number, F.text)
async def get_message(message: Message, state: FSMContext):
    await state.update_data(number = message.text)
    await state.set_state(Form.await_msg_email)
    await message.answer(text=needhelp3_text)

@dp.message(Form.await_msg_email, F.text)
async def send_message(message: Message, state: FSMContext) -> None:
    await message.answer(text=success_reg_text, reply_markup=main_reply_kb)
    await state.update_data(email = message.text)
    username = message.from_user.username
    data = await state.get_data()
    types, number, email = data["type"], data["number"], data["email"]
    await bot.send_message(chat_id, f"Пользователь @{username} подал заявку\nТип заявки: {types}\nНомер телефона: {number}\nПочта: {email}")
    await state.clear()

@dp.callback_query(F.data == "Обратная связь")
async def feedback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Напиши свой отзыв")
    await state.set_state(Feedback.feedback)

@dp.message(Feedback.feedback)
async def send_feedback(message: Message, state: FSMContext):
    await message.answer(text="Спасибо за Ваш отзыв")
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute(f'''SELECT * FROM "intensive" WHERE tg_id='{message.from_user.id}';''')
    users = cursor.fetchone()
    connection.close()
    day = (datetime.now() - datetime(users[2].year, users[2].month, users[2].day)).days
    days = ["первого", "второго", "третьего", "четвертого", "пятого", "шестого", "седьмого"]
    await bot.send_message(chat_id=chat_id, text=feedback_text_mes.format(username=message.from_user.username, day=days[day], feedback=message.text))

def new_day():
    loop = new_event_loop()
    set_event_loop(loop)
    days_func = [second_day_of_intensive, third_day_of_intensive, fourth_day_of_intensive, fiveth_day_of_intensive, sixth_day_of_intensive, seventh_day_of_intensive]
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute(f'''SELECT * FROM "intensive"''')
    users = cursor.fetchall()
    connection.close()
    mail = []
    for i in users:
        if i[1] not in mail:
            mail.append(i[1])
            day = datetime.now() - datetime(i[2].year, i[2].month, i[2].day)
            day = min(max(1, day.days), 6)
            loop.run_until_complete(days_func[day - 1](i[1]))
            loop.run_until_complete(bot.send_message(chat_id=i[1], text=feedback_text, reply_markup=feedback_kb()))
    system("systemctl restart intensiveday")
    

async def first_day_of_intensive(tg_id):
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute(f'''INSERT INTO "intensive" (tg_id) VALUES ('{tg_id}')''')
    connection.commit()
    connection.close()
    await bot.send_photo(chat_id=tg_id, photo=intensive_hello_photo, caption=intensive_hello_text)
    await bot.send_message(chat_id=tg_id, text=intensive_day1_text1)
    await bot.send_photo(chat_id=tg_id, photo=intensive_day1_photo, caption=intensive_day1_text2)

async def second_day_of_intensive(tg_id):
    await bot.send_audio(chat_id=tg_id, audio=intensive_day2_audio1, caption=intensive_day2_text1)
    media = MediaGroupBuilder(caption=intensive_day2_text2)
    media.add_photo(media=intensive_day2_photo1)
    media.add_photo(media=intensive_day2_photo2)
    media.add_photo(media=intensive_day2_photo3)
    media.add_photo(media=intensive_day2_photo4)
    media.add_photo(media=intensive_day2_photo5)
    media.add_photo(media=intensive_day2_photo6)
    media.add_photo(media=intensive_day2_photo7)
    media.add_photo(media=intensive_day2_photo8)
    await bot.send_media_group(chat_id=tg_id, media=media.build())
    await bot.send_audio(chat_id=tg_id, audio=intensive_day2_audio2, caption=intensive_day2_text3)

async def third_day_of_intensive(tg_id):
    await bot.send_message(chat_id=tg_id, text=intensive_day3_text1)
    await bot.send_document(chat_id=tg_id, document=intensive_day3_file)
    media = MediaGroupBuilder(caption=intensive_day3_text2)
    media.add_photo(media=intensive_day3_photo1)
    media.add_photo(media=intensive_day3_photo2)
    await bot.send_media_group(chat_id=tg_id, media=media.build())
    await bot.send_message(chat_id=tg_id, text=intensive_day3_text3)

async def fourth_day_of_intensive(tg_id):
    await bot.send_message(chat_id=tg_id, text=intensive_day4_text1)
    await bot.send_audio(chat_id=tg_id, audio=intensive_day4_audio1, caption=intensive_day4_text2)
    await bot.send_photo(chat_id=tg_id, photo=intensive_day4_photo1, caption=intensive_day4_text3)
    await bot.send_audio(chat_id=tg_id, audio=intensive_day4_audio2, caption=intensive_day4_text4)
    await bot.send_audio(chat_id=tg_id, audio=intensive_day4_audio3, caption=intensive_day4_text5)

async def fiveth_day_of_intensive(tg_id):
    await bot.send_message(chat_id=tg_id, text=intensive_day5_text1)
    await bot.send_message(chat_id=tg_id, text=intensive_day5_text2)
    media = MediaGroupBuilder()
    media.add_photo(media=intensive_day5_photo1)
    media.add_photo(media=intensive_day5_photo2)
    media.add_photo(media=intensive_day5_photo3)
    media.add_photo(media=intensive_day5_photo4)
    media.add_photo(media=intensive_day5_photo5)
    media.add_photo(media=intensive_day5_photo6)
    media.add_photo(media=intensive_day5_photo7)
    media.add_photo(media=intensive_day5_photo8)
    media.add_photo(media=intensive_day5_photo9)
    await bot.send_media_group(chat_id=tg_id, media=media.build())
    await bot.send_message(chat_id=tg_id, text=intensive_day5_text3)
    await bot.send_message(chat_id=tg_id, text=intensive_day5_text4)

async def sixth_day_of_intensive(tg_id):
    await bot.send_audio(chat_id=tg_id, audio=intensive_day6_audio1, caption=intensive_day6_text1)
    await bot.send_message(chat_id=tg_id, text=intensive_day6_text2)

async def seventh_day_of_intensive(tg_id):
    await bot.send_message(chat_id=tg_id, text=intensive_day7_text1)
    await bot.send_audio(chat_id=tg_id, audio=intensive_day7_audio1, caption=intensive_day7_text2)
    media = MediaGroupBuilder(caption=intensive_day7_text3)
    media.add_photo(media=intensive_day7_photo1)
    media.add_video(media=intensive_day7_video1)
    await bot.send_media_group(chat_id=tg_id, media=media.build())
    await bot.send_photo(chat_id=tg_id, photo=intensive_final_photo, caption=intensive_final_text)
    connection = connect(config_1.POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute(f'''DELETE FROM "intensive" WHERE tg_id = '{tg_id}';''')
    connection.commit()
    connection.close()

# async def main(tg_id):
#     await first_day_of_intensive(tg_id)
#     await second_day_of_intensive(tg_id)
#     await third_day_of_intensive(tg_id)
#     await fourth_day_of_intensive(tg_id)
#     await fiveth_day_of_intensive(tg_id)
#     await sixth_day_of_intensive(tg_id)
#     await seventh_day_of_intensive(tg_id)

# loop = new_event_loop()
# set_event_loop(loop)
# loop.run_until_complete(main("6189886745"))