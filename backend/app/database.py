from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


def ensure_database_exists():
    url = make_url(settings.database_url)
    if not url.drivername.startswith("mysql") or not url.database:
        return

    database_name = url.database
    server_url = url.set(database="")
    server_engine = create_engine(server_url, pool_pre_ping=True)
    quoted_database = database_name.replace("`", "``")
    with server_engine.connect() as connection:
        connection.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{quoted_database}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
    server_engine.dispose()


ensure_database_exists()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upgrade_schema():
    """Add columns introduced after the initial tables were deployed."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    statements = []
    if "care_orders" in table_names:
        order_columns = {column["name"] for column in inspector.get_columns("care_orders")}
        if "employee_id" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN employee_id INTEGER NULL")
        if "accepted_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN accepted_at DATETIME NULL")
        if "started_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN started_at DATETIME NULL")
        if "completed_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN completed_at DATETIME NULL")
        if "stopped_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN stopped_at DATETIME NULL")
    if "employees" in table_names:
        employee_columns = {column["name"] for column in inspector.get_columns("employees")}
        if "username" not in employee_columns:
            statements.append("ALTER TABLE employees ADD COLUMN username VARCHAR(50) NULL")
        if "password_hash" not in employee_columns:
            statements.append("ALTER TABLE employees ADD COLUMN password_hash VARCHAR(255) NULL")
    if not statements:
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
