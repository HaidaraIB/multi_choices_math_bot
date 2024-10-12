import sqlalchemy as sa
from sqlalchemy.orm import Session, relationship, backref
from models.DB import Base, lock_and_release


class TestQuestion(Base):
    __tablename__ = "test_questions"
    test_id = sa.Column(
        sa.Integer, sa.ForeignKey("test_results.id", ondelete="CASCADE")
    )
    cat_id = sa.Column(
        sa.Integer, sa.ForeignKey("test_results.cat_id", ondelete="CASCADE")
    )
    q_id = sa.Column(sa.Integer)

    category = relationship(
        "TestResult", backref=backref("test_questions", passive_deletes=True)
    )

    @classmethod
    @lock_and_release
    async def add(cls, q_ids: list[int], test_id: int, cat_id: int, s: Session = None):
        for q_id in q_ids:
            s.execute(
                sa.insert(cls).values(
                    q_id=q_id,
                    test_id=test_id,
                    cat_id=cat_id,
                )
            )
