import sqlalchemy as sa
from sqlalchemy.orm import Session, relationship, backref
from models.DB import Base, lock_and_release, connect_and_close


class Choice(Base):
    __tablename__ = "choices"
    id = sa.Column(sa.Integer)
    q_id = sa.Column(sa.Integer, sa.ForeignKey("questions.id", ondelete="CASCADE"))
    choice = sa.Column(sa.String)
    is_correct = sa.Column(sa.Boolean, default=False)

    __table_args__ = (
        sa.PrimaryKeyConstraint(
            "id",
            "q_id",
            name="choice_pk",
        ),
    )

    question = relationship(
        "Question", backref=backref("choices", passive_deletes=True)
    )

    @classmethod
    def inner_add(
        cls,
        q_id: int,
        choice: str,
        s: Session = None,
    ):
        res = s.execute(sa.select(sa.func.max(cls.id)).where(cls.q_id == q_id))
        count = res.fetchone().t[0]
        s.execute(
            sa.insert(cls).values(
                q_id=q_id,
                choice=choice,
                id=count + 1 if count else 1,
            )
        )

    @classmethod
    @lock_and_release
    async def add(
        cls,
        q_id: int,
        choice: str,
        is_correct: bool = False,
        s: Session = None,
    ):
        res = s.execute(sa.select(sa.func.max(cls.id)).where(cls.q_id == q_id))
        count = res.fetchone().t[0]
        if is_correct:
            s.query(cls).filter_by(q_id=q_id).update({cls.is_correct: 0})
            s.execute(
                sa.insert(cls).values(
                    q_id=q_id,
                    choice=choice,
                    is_correct=is_correct,
                    id=count + 1 if count else 1,
                )
            )
        else:
            s.execute(
                sa.insert(cls).values(
                    q_id=q_id,
                    choice=choice,
                    id=count + 1 if count else 1,
                )
            )

    @classmethod
    @lock_and_release
    async def update(cls, c_id: int, q_id: int, field: str, value, s: Session = None):
        s.query(cls).filter_by(id=c_id, q_id=q_id).update(
            {
                getattr(cls, field): value,
            }
        )

    @classmethod
    @connect_and_close
    def get_by(
        cls, q_id: int, c_id: int = None, correct: bool = None, s: Session = None
    ):
        if c_id:
            res = s.execute(
                sa.select(cls).where(
                    sa.and_(
                        cls.id == c_id,
                        cls.q_id == q_id,
                    )
                )
            )
            try:
                return res.fetchone().t[0]
            except:
                pass
        elif q_id:
            res = s.execute(sa.select(cls).where(cls.q_id == q_id))
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass
        elif correct:
            res = s.execute(
                sa.select(cls).where(
                    sa.and_(
                        cls.q_id == q_id,
                        cls.id == c_id,
                        cls.is_correct == True,
                    )
                )
            )
            try:
                return res.fetchone().t[0]
            except:
                pass

    @classmethod
    @lock_and_release
    async def delete(cls, choice_id: int, q_id: int, s: Session = None):
        # Delete the coice
        s.execute(
            sa.delete(cls).where(
                sa.and_(
                    cls.id == choice_id,
                    cls.q_id == q_id,
                )
            )
        )

        # Preserve the sequential order by updating bigger ids.
        s.query(cls).filter(
            cls.q_id == q_id,
            cls.id > choice_id,
        ).update(
            {
                cls.id: cls.id - 1,
            }
        )
