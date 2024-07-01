from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from datetime import datetime
from media import *
from modules.Pay_system import Prodamus
from aiogram.types import WebAppInfo
from psycopg2 import connect
from config import config_1


PAY_URL = 'ssomova.payform.ru'
SECRET_KEY = '4172825dea26e2f400e574228c4b3959ee2c8acbf21d4f914452014abb273f12'

def admin_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Хотите попробовать функции юзера?", callback_data="Хотите попробовать функции юзера?"
    )
    builder.button(
        text="Настроить рассылку", callback_data="Настроить рассылку"
    )
    builder.adjust(1)
    return builder.as_markup()

main_reply_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Интенсив"), KeyboardButton(text="Личная работа")]],
    resize_keyboard=True
)

def are_you_sure():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да", callback_data="Да"
    )
    builder.button(
        text="Нет", callback_data="Нет"
    )
    builder.adjust(1)
    return builder.as_markup()

def give_start_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Узнать больше про мой опыт", callback_data="Обо мне"
    )
    builder.button(
        text="Получить урок", callback_data="Получить урок"
    )

    builder.adjust(1)
    return builder.as_markup()

def give_prodamus_link(id):
    products = {'name': 'Оплата интенсива',
                'price': 50,
                'quantity': 1,
                }
    this_time = datetime.now().strftime("%d%m%Y%H%M%S")
    data = {'order_id': str(id) + this_time[:4] + this_time[6:8] + this_time[9:],
            'customer_extra': customer_extra,
            }
    connection = Prodamus.Prodamus(PAY_URL, SECRET_KEY)
    intensive_pay = Prodamus.Order(connection, products, data)
    connection_sql = connect(config_1.POSTGRES_URL)
    cursor = connection_sql.cursor()
    cursor.execute(f'''INSERT INTO "order" (tg_id, caption, status) VALUES ('{id}', '{intensive_pay.get_sign()}', 'wait')''')
    connection_sql.commit()
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Оплатить", web_app=WebAppInfo(url=intensive_pay.create_pay_link())
    )
    builder.adjust(1)
    return builder.as_markup()

def feedback_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Обратная связь", callback_data="Обратная связь"
    )

    builder.adjust(1)
    return builder.as_markup()

def lesson_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Получить урок", callback_data="Получить урок"
    )

    builder.adjust(1)
    return builder.as_markup()

def reaction_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="👍🏻", callback_data="лайк"
    )
    builder.button(
        text="👎🏻", callback_data="дизлайк"
    )

    builder.adjust(2)
    return builder.as_markup()

def product_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Узнать про интенсив за 990₽", callback_data="Интенсив"
    )
    builder.button(
        text="Узнать про форматы личной работы", callback_data="Личная работа"
    )

    builder.adjust(1)
    return builder.as_markup()

def intensive_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Оплатить", callback_data="Оплатить интенсив"
    )

    builder.adjust(1)
    return builder.as_markup()

def club_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Записаться на презентацию", callback_data="Записаться на презентацию"
    )


    builder.adjust(1)
    return builder.as_markup()

def personal_work_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Записаться", callback_data="Личные"
    )


    builder.adjust(1)
    return builder.as_markup()