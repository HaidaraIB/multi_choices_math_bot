import sqlalchemy as sa
from sqlalchemy.orm import Session, relationship, backref
from models.DB import Base, lock_and_release, connect_and_close


class Channel(Base):
    __tablename__ = "channels"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)

    @classmethod
    @lock_and_release
    async def add(cls, i: int, title: str, s: Session = None):
        s.execute(sa.insert(cls).values(id=i, title=title))

    @classmethod
    @lock_and_release
    async def update(cls, i: int, new_title: str, s: Session = None):
        s.query(cls).filter_by(id=i).update({cls.title: new_title})

    @classmethod
    @connect_and_close
    def get_by(cls, i: int = None, s: Session = None):
        if i:
            res = s.execute(sa.select(cls).where(cls.id == i))
            try:
                return res.fetchone().t[0]
            except:
                pass
        else:
            res = s.execute(sa.select(cls))
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass
