from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Print SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before using
    pool_recycle=3600     # Recycle connections every hour
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        return
    except OperationalError as e:
        # If the database itself doesn't exist yet (common in fresh dev setups),
        # create it and retry table creation.
        if _is_unknown_database_error(e) and _create_database_if_missing():
            Base.metadata.create_all(bind=engine)
            return
        raise


def _is_unknown_database_error(err: OperationalError) -> bool:
    # PyMySQL: (1049, "Unknown database 'cliniq_db'")
    msg = str(err).lower()
    if "unknown database" in msg:
        return True
    orig = getattr(err, "orig", None)
    if orig is not None:
        args = getattr(orig, "args", ())
        if isinstance(args, tuple) and args:
            code = args[0]
            if code == 1049:
                return True
    return False


def _create_database_if_missing() -> bool:
    url = make_url(settings.DATABASE_URL)
    db_name = url.database
    if not db_name:
        return False

    # Connect without selecting a database, so we can create it.
    server_url = url.set(database=None)
    tmp_engine = create_engine(
        server_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    try:
        with tmp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
            conn.commit()
        return True
    finally:
        tmp_engine.dispose()
