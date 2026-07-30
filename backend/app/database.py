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
        if "review_token" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN review_token VARCHAR(64) NULL")
        if "customer_location_updated_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN customer_location_updated_at DATETIME NULL")
        if "staff_latitude" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN staff_latitude DECIMAL(10, 7) NULL")
        if "staff_longitude" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN staff_longitude DECIMAL(10, 7) NULL")
        if "staff_location_updated_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN staff_location_updated_at DATETIME NULL")
        if "early_finish_requested_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN early_finish_requested_at DATETIME NULL")
        if "early_finish_response" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN early_finish_response BOOLEAN NULL")
        if "early_finish_responded_at" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN early_finish_responded_at DATETIME NULL")
        if "commission_rate" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN commission_rate DECIMAL(5, 2) NULL")
        if "staff_earning_cents" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN staff_earning_cents INTEGER NULL")
        if "completion_type" not in order_columns:
            statements.append("ALTER TABLE care_orders ADD COLUMN completion_type VARCHAR(40) NULL")
    if "employees" in table_names:
        employee_columns = {column["name"] for column in inspector.get_columns("employees")}
        if "username" not in employee_columns:
            statements.append("ALTER TABLE employees ADD COLUMN username VARCHAR(50) NULL")
        if "password_hash" not in employee_columns:
            statements.append("ALTER TABLE employees ADD COLUMN password_hash VARCHAR(255) NULL")
        if "employee_code" not in employee_columns:
            statements.append("ALTER TABLE employees ADD COLUMN employee_code VARCHAR(50) NULL")
        if "commission_rate" not in employee_columns:
            statements.append("ALTER TABLE employees ADD COLUMN commission_rate DECIMAL(5, 2) NULL")
        if "role" not in employee_columns:
            statements.append("ALTER TABLE employees ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'caregiver'")
    if "products" not in table_names:
        if engine.dialect.name == "mysql":
            statements.append(
                "CREATE TABLE products ("
                "id INTEGER PRIMARY KEY AUTO_INCREMENT, "
                "name VARCHAR(120) NOT NULL, "
                "category VARCHAR(50) NULL, "
                "description TEXT NULL, "
                "price_cents INTEGER NOT NULL, "
                "stock INTEGER NOT NULL DEFAULT 0, "
                "sales_count INTEGER NOT NULL DEFAULT 0, "
                "cover VARCHAR(20) NOT NULL, "
                "is_active BOOLEAN NOT NULL DEFAULT TRUE, "
                "created_at DATETIME NULL, "
                "updated_at DATETIME NULL, "
                "INDEX ix_products_name (name), "
                "INDEX ix_products_category (category), "
                "INDEX ix_products_is_active (is_active)"
                ")"
            )
        else:
            statements.extend(
                [
                    "CREATE TABLE products ("
                    "id INTEGER PRIMARY KEY, "
                    "name VARCHAR(120) NOT NULL, "
                    "category VARCHAR(50) NULL, "
                    "description TEXT NULL, "
                    "price_cents INTEGER NOT NULL, "
                    "stock INTEGER NOT NULL DEFAULT 0, "
                    "sales_count INTEGER NOT NULL DEFAULT 0, "
                    "cover VARCHAR(20) NOT NULL, "
                    "is_active BOOLEAN NOT NULL DEFAULT 1, "
                    "created_at DATETIME NULL, "
                    "updated_at DATETIME NULL"
                    ")",
                    "CREATE INDEX ix_products_name ON products (name)",
                    "CREATE INDEX ix_products_category ON products (category)",
                    "CREATE INDEX ix_products_is_active ON products (is_active)",
                ]
            )
    if "mall_orders" not in table_names:
        if engine.dialect.name == "mysql":
            statements.append(
                "CREATE TABLE mall_orders ("
                "id INTEGER PRIMARY KEY AUTO_INCREMENT, "
                "order_no VARCHAR(32) NOT NULL UNIQUE, "
                "access_token VARCHAR(64) NOT NULL UNIQUE, "
                "product_id INTEGER NOT NULL, "
                "product_name VARCHAR(120) NOT NULL, "
                "product_cover VARCHAR(20) NOT NULL, "
                "unit_price_cents INTEGER NOT NULL, "
                "quantity INTEGER NOT NULL, "
                "amount_cents INTEGER NOT NULL, "
                "status VARCHAR(30) NOT NULL, "
                "created_at DATETIME NULL, "
                "paid_at DATETIME NULL, "
                "INDEX ix_mall_orders_product_id (product_id), "
                "INDEX ix_mall_orders_status (status), "
                "INDEX ix_mall_orders_created_at (created_at), "
                "FOREIGN KEY(product_id) REFERENCES products (id)"
                ")"
            )
        else:
            statements.extend(
                [
                    "CREATE TABLE mall_orders ("
                    "id INTEGER PRIMARY KEY, "
                    "order_no VARCHAR(32) NOT NULL UNIQUE, "
                    "access_token VARCHAR(64) NOT NULL UNIQUE, "
                    "product_id INTEGER NOT NULL, "
                    "product_name VARCHAR(120) NOT NULL, "
                    "product_cover VARCHAR(20) NOT NULL, "
                    "unit_price_cents INTEGER NOT NULL, "
                    "quantity INTEGER NOT NULL, "
                    "amount_cents INTEGER NOT NULL, "
                    "status VARCHAR(30) NOT NULL, "
                    "created_at DATETIME NULL, "
                    "paid_at DATETIME NULL, "
                    "FOREIGN KEY(product_id) REFERENCES products (id)"
                    ")",
                    "CREATE INDEX ix_mall_orders_product_id ON mall_orders (product_id)",
                    "CREATE INDEX ix_mall_orders_status ON mall_orders (status)",
                    "CREATE INDEX ix_mall_orders_created_at ON mall_orders (created_at)",
                ]
            )
    if "order_messages" not in table_names:
        if engine.dialect.name == "mysql":
            statements.append(
                "CREATE TABLE order_messages ("
                "id INTEGER PRIMARY KEY AUTO_INCREMENT, "
                "order_id INTEGER NOT NULL, "
                "sender_type VARCHAR(20) NOT NULL, "
                "sender_id INTEGER NULL, "
                "sender_name VARCHAR(50) NOT NULL, "
                "content TEXT NOT NULL, "
                "created_at DATETIME NULL, "
                "INDEX ix_order_messages_order_id (order_id), "
                "INDEX ix_order_messages_sender_type (sender_type), "
                "INDEX ix_order_messages_created_at (created_at), "
                "FOREIGN KEY(order_id) REFERENCES care_orders (id)"
                ")"
            )
        else:
            statements.extend(
                [
                    "CREATE TABLE order_messages ("
                    "id INTEGER PRIMARY KEY, "
                    "order_id INTEGER NOT NULL, "
                    "sender_type VARCHAR(20) NOT NULL, "
                    "sender_id INTEGER NULL, "
                    "sender_name VARCHAR(50) NOT NULL, "
                    "content TEXT NOT NULL, "
                    "created_at DATETIME NULL, "
                    "FOREIGN KEY(order_id) REFERENCES care_orders (id)"
                    ")",
                    "CREATE INDEX ix_order_messages_order_id ON order_messages (order_id)",
                    "CREATE INDEX ix_order_messages_sender_type ON order_messages (sender_type)",
                    "CREATE INDEX ix_order_messages_created_at ON order_messages (created_at)",
                ]
            )
    if "employee_income_records" not in table_names:
        if engine.dialect.name == "mysql":
            statements.append(
                "CREATE TABLE employee_income_records ("
                "id INTEGER PRIMARY KEY AUTO_INCREMENT, "
                "employee_id INTEGER NOT NULL, "
                "order_id INTEGER NOT NULL UNIQUE, "
                "amount_cents INTEGER NOT NULL, "
                "status VARCHAR(20) NOT NULL, "
                "created_at DATETIME NULL, "
                "INDEX ix_employee_income_records_employee_id (employee_id), "
                "INDEX ix_employee_income_records_status (status), "
                "INDEX ix_employee_income_records_created_at (created_at), "
                "FOREIGN KEY(employee_id) REFERENCES employees (id), "
                "FOREIGN KEY(order_id) REFERENCES care_orders (id)"
                ")"
            )
        else:
            statements.extend(
                [
                    "CREATE TABLE employee_income_records ("
                    "id INTEGER PRIMARY KEY, "
                    "employee_id INTEGER NOT NULL, "
                    "order_id INTEGER NOT NULL UNIQUE, "
                    "amount_cents INTEGER NOT NULL, "
                    "status VARCHAR(20) NOT NULL, "
                    "created_at DATETIME NULL, "
                    "FOREIGN KEY(employee_id) REFERENCES employees (id), "
                    "FOREIGN KEY(order_id) REFERENCES care_orders (id)"
                    ")",
                    "CREATE INDEX ix_employee_income_records_employee_id ON employee_income_records (employee_id)",
                    "CREATE INDEX ix_employee_income_records_status ON employee_income_records (status)",
                    "CREATE INDEX ix_employee_income_records_created_at ON employee_income_records (created_at)",
                ]
            )
    if not statements:
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
