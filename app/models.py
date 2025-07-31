from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class JeopardyQuestion(Base):
    __tablename__ = 'jeopardy_questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    show_number = Column(Integer)
    air_date = Column(String)
    round = Column(String)
    category = Column(String)
    value = Column(Integer)
    question = Column(Text)
    answer = Column(Text)