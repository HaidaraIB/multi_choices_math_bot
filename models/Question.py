import sqlalchemy as sa
from sqlalchemy.orm import Session, relationship, backref
from models.DB import Base, lock_and_release, connect_and_close
from models.Choice import Choice


class Question(Base):
    __tablename__ = "questions"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    category_id = sa.Column(
        sa.Integer, sa.ForeignKey("categories.id", ondelete="CASCADE")
    )
    q = sa.Column(sa.String)
    category = relationship(
        "Category", backref=backref("questions", passive_deletes=True)
    )

    @classmethod
    @lock_and_release
    async def add(
        cls, q: str, category_id: int, choices: list[str] = None, s: Session = None
    ):
        res = s.execute(
            sa.insert(cls).values(
                q=q,
                category_id=category_id,
            )
        )
        if choices:
            for choice in choices:
                Choice.inner_add(q_id=res.lastrowid, choice=choice, s=s)

        return res.lastrowid

    @classmethod
    @connect_and_close
    def get_by(
        cls, q_id: int = None, cat_id: int = None, limit: int = None, s: Session = None
    ):
        if q_id:
            res = s.execute(sa.select(cls).where(cls.id == q_id))
            try:
                return res.fetchone().t[0]
            except:
                pass
        elif cat_id:
            if limit:
                res = s.execute(
                    sa.select(cls).where(cls.category_id == cat_id).limit(limit)
                )
            else:
                res = s.execute(sa.select(cls).where(cls.category_id == cat_id))

        else:
            res = s.execute(sa.select(cls))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass

    @classmethod
    @lock_and_release
    async def delete(cls, q_id: int, s: Session = None):
        s.execute(sa.delete(cls).where(cls.id == q_id))

    @classmethod
    @lock_and_release
    async def update(cls, q_id: int, field: str, value, s: Session = None):
        s.query(cls).filter_by(id=q_id).update(
            {
                getattr(cls, field): value,
            }
        )
