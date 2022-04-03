import sqlalchemy as db

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = db.create_engine("sqlite:///items.db")  # Create test.sqlite automatically
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


class Items(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    price = Column(String)
    title = Column(String)
    section = Column(String)
    subsection = Column(String)
    description = Column(String, nullable=True)
    energy = Column(String, nullable=True)
    calories = Column(String, nullable=True)
    fat = Column(String, nullable=True)
    saturated_fat = Column(String, nullable=True)
    unsaturated_fat = Column(String, nullable=True)
    polyunsaturated_fat = Column(String, nullable=True)
    carbs = Column(String, nullable=True)
    sugar = Column(String, nullable=True)
    starch = Column(String, nullable=True)
    fiber = Column(String, nullable=True)
    protein = Column(String, nullable=True)
    salt = Column(String, nullable=True)

    def __repr__(self):
        return f"Title {self.title}, {self.descrition}"


Base.metadata.create_all(engine)


def add_item(
    price="",
    title="",
    section="",
    subsection="",
    description="",
    energy="",
    calories="",
    fat="",
    saturated_fat="",
    unsaturated_fat="",
    polyunsaturated_fat="",
    carbs="",
    sugar="",
    starch="",
    fiber="",
    protein="",
    salt="",
):
    db_items = Items(
        price=price,
        title=title,
        section=section,
        subsection=subsection,
        description=description,
        energy=energy,
        calories=calories,
        fat=fat,
        saturated_fat=saturated_fat,
        unsaturated_fat=unsaturated_fat,
        polyunsaturated_fat=polyunsaturated_fat,
        carbs=carbs,
        sugar=sugar,
        starch=starch,
        fiber=fiber,
        protein=protein,
        salt=salt,
    )
    session.add(db_items)
    session.commit()
