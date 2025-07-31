import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = "postgresql+psycopg2://admin:super-secret-password@localhost:5432/wwtba"

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


def clean_value(value) -> int:
    if isinstance(value, str):
        try:
            return int(value.replace('$', '').replace(',', '').split('.')[0])
        except (ValueError, AttributeError):
            return 0
    return 0


def import_data():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        session.query(JeopardyQuestion).delete()

        df = pd.read_csv('data/JEOPARDY_CSV.csv', quotechar='"')
        df.columns = [col.strip() for col in df.columns]

        df['Cleaned Value'] = df['Value'].apply(clean_value)
        filtered_df = df[df['Cleaned Value'] <= 1200]

        for _, row in filtered_df.iterrows():
            if not isinstance(row['Cleaned Value'], int):
                continue
            question_record = JeopardyQuestion(
                show_number=row['Show Number'],
                air_date=row['Air Date'],
                round=row['Round'],
                category=row['Category'],
                value=row['Cleaned Value'],
                question=row['Question'],
                answer=row['Answer']
            )
            session.add(question_record)

        session.commit()
        print(f"Database reset and successfully imported {len(filtered_df)} questions.")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    import_data()
