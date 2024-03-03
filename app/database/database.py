from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.load_env import config


engine = create_engine(
    url=config.DB_URL,
    pool_size=int(config.POOL_SIZE),
    max_overflow=int(config.MAX_OVERFLOW),
    pool_pre_ping=bool(config.POOL_PRE_PING),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
