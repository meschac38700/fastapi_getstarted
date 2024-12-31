from sqlalchemy import create_engine

from settings import DatabaseSettings

db = DatabaseSettings()

engine = create_engine(
    f"postgresql+psycopg2://{db.user}:{db.password}@{db.host}/{db.name}"
)
