import asyncio
from gino import Gino

db = Gino()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    nickname = db.Column(db.Unicode(), default='noname')


async def setup():
    print("DB Setup")
    await db.set_bind('postgresql://postgres:jokalive@localhost/gino')

    # Create tables
    await db.gino.create_all()


async def task(params):
    # Create object, `id` is assigned by database
    u = await User.create(**params)
    print(u.id, u.nickname)  # 1 fantix
    return as_dict(u)


def as_dict(model):
    return {c.name: str(getattr(model, c.name)) for c in model.__table__.columns}
