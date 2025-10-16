import os
from sqlalchemy import text


def init_database_schema(db, project_base_dir):
    """Initialize database schema from schema.sql for pgvector support"""
    try:
        if 'postgresql' in db.engine.url.drivername:
            print("🔧 Checking database schema...")
            
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            db.session.commit()
            print("✓ pgvector extension enabled")
            
            schema_path = os.path.join(project_base_dir, "database", "schema.sql")
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                db.session.execute(text(schema_sql))
                db.session.commit()
                print("✓ Database schema initialized successfully")
            else:
                print("⚠️  Schema file not found, skipping schema initialization")
        else:
            print("ℹ️  Using SQLite, skipping pgvector schema initialization")
    except Exception as e:
        print(f"⚠️  Error initializing database schema: {e}")
        pass