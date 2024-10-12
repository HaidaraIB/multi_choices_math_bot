import sqlalchemy as sa
from sqlalchemy.orm import relationship, Session, backref
from models.DB import Base, lock_and_release, connect_and_close


class TestResult(Base):
    __tablename__ = "test_results"
    test_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"))
    cat_id = sa.Column(sa.Integer, sa.ForeignKey("categories.id", ondelete="CASCADE"))
    result = sa.Column(sa.Float)

    category = relationship(
        "Category", backref=backref("test_results", passive_deletes=True)
    )
    user = relationship("User", backref=backref("test_results", passive_deletes=True))

    @classmethod
    @lock_and_release
    async def add(cls, user_id: int, cat_id: int, result: float, s: Session = None):
        res = s.execute(
            sa.insert(cls).values(
                user_id=user_id,
                cat_id=cat_id,
                result=result,
            )
        )
        return res.lastrowid
