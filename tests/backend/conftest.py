import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import csv
import os

# Use the actual database and models from the application
from app.persistance import DATABASE_URL
from app.models import Base, JeopardyQuestion

# Create an engine that connects to the application's database
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def load_test_data_from_csv(db_session):
    """Helper function to load data from CSV into the test DB."""
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'sample_test_data.csv')

    with open(csv_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                value = int(row['value'])
            except (ValueError, TypeError):
                value = None

            question = JeopardyQuestion(
                id=int(row['id']),
                show_number=int(row['show_number']),
                air_date=row['air_date'],
                round=row['round'],
                category=row['category'],
                value=value,
                question=row['question'],
                answer=row['answer'],
            )
            db_session.add(question)
    db_session.commit()

@pytest.fixture(scope="function")
def setup_database() -> Generator:
    """
    Fixture to set up the live database for an E2E test run.

    It creates all tables, loads data from a CSV, yields control to the
    test, and then tears down (drops) the tables to ensure a clean state.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Populate with sample data
    load_test_data_from_csv(db)

    try:
        yield
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
