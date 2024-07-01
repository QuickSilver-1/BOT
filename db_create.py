from asyncio import new_event_loop, set_event_loop
from config import config_1
from database import db, Order


async def db_create():
    await db.set_bind(config_1.POSTGRES_URL)
    await db.gino.drop_all()
    await db.gino.create_all()
    

async def create_order(tg_id, caption, wait_pay):
    await db.set_bind(config_1.POSTGRES_URL)
    order = Order(tg_id=tg_id, caption=caption, status=wait_pay)
    await order.create()


async def db_test():
    await db_create()
    #await create_order("1051818216", "89228884485", "wait_pay")

loop = new_event_loop()
set_event_loop(loop)
loop.run_until_complete(db_test())
