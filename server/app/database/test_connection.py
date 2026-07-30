from sqlalchemy import text
from app.database.session import engine

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("✅ PostgreSQL connected successfully!")
except Exception as e:
    print("❌ Connection failed")
    print(e)