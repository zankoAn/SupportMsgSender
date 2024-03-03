from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, Session
from app.utils.load_env import config


engine = create_engine(
    url=config.DB_URL,
    pool_size=int(config.POOL_SIZE),
    max_overflow=int(config.MAX_OVERFLOW),
    pool_pre_ping=bool(config.POOL_PRE_PING),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SessionManager:
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.db.rollback()
        except exc.SQLAlchemyError:
            pass
        finally:
            self.db.close()