import sqlalchemy as sa
from sqlalchemy.orm import Session, relationship
from models.DB import Base, lock_and_release, connect_and_close


class Category(Base):
    __tablename__ = "categories"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, unique=True)

    @classmethod
    @lock_and_release
    async def delete(cls, cat_id: int, s: Session = None):
        s.execute(sa.delete(cls).where(cls.id == cat_id))

    @classmethod
    @lock_and_release
    async def add(cls, name: str, s: Session = None):
        s.execute(sa.insert(cls).values(name=name).prefix_with("OR IGNORE"))

    @classmethod
    @connect_and_close
    def get_by(cls, cat_id: int = None, s: Session = None):
        if cat_id:
            res = s.execute(sa.select(cls).where(cls.id == cat_id))
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
