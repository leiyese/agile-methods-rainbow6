# backend/run_init_docs.py
import os
from pathlib import Path
from types import SimpleNamespace
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

url = os.getenv("DATABASE_URL")
assert url and url.startswith("postgresql"), f"Bad DATABASE_URL: {url}"
engine = create_engine(url)
Session = scoped_session(sessionmaker(bind=engine))
db = SimpleNamespace(engine=engine, session=Session())

project_base_dir = str(Path(__file__).resolve().parent)

from database.init_documents import init_documents
init_documents(db, project_base_dir)

db.session.close()
print("Done.")