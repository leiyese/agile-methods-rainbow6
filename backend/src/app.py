import os
import sys

# Add the directory containing this script to sys.path
# This allows for absolute imports relative to the 'src' directory
script_dir = os.path.dirname(__file__)
project_base_dir = os.path.dirname(script_dir)
if project_base_dir not in sys.path:
    sys.path.insert(0, project_base_dir)

import json
from flask import Flask
from src.extensions import db, cors
from src.blueprints.main import bp as main_bp
from src.blueprints.assistant import bp as assistant_bp

# import llm wrapper
from agents.llm_wrapper import GeminiLLM

from sqlalchemy import text


def create_app():
    app = Flask(__name__, template_folder="templates")

    # Initialiserar LLM modellen
    app.config["LLM"] = GeminiLLM()

    raw_url = os.environ.get("DATABASE_URL")
    if raw_url and raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = raw_url or "sqlite:///rainbow6.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.setdefault(
        "SQLALCHEMY_ENGINE_OPTIONS",
        {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        },
    )

    db.init_app(app)

    is_prod = (
        os.environ.get("FLASK_ENV") == "production"
        or os.environ.get("RENDER") == "true"
    )
    if is_prod:
        frontend_url = os.environ.get("FRONTEND_URL")
        if frontend_url:
            cors.init_app(app, origins=[frontend_url])
        else:
            cors.init_app(app, origins=[])
    else:
        cors.init_app(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    try:
        copy_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "copy.json"
        )
        with open(copy_path, "r", encoding="utf-8") as f:
            app.config["COPY"] = json.load(f)
    except FileNotFoundError:
        app.config["COPY"] = {}
    except json.JSONDecodeError:
        app.config["COPY"] = {}

    app.register_blueprint(main_bp)
    app.register_blueprint(assistant_bp)

    with app.app_context():
        db.create_all()
        
        init_database_schema()
        init_documents()

    return app


def init_database_schema():
    """Initialize database schema from schema.sql for pgvector support"""
    try:
        # Only run for PostgreSQL databases
        if 'postgresql' in db.engine.url.drivername:
            print("🔧 Checking database schema...")
            
            # First, ensure pgvector extension is enabled
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            db.session.commit()
            print("✓ pgvector extension enabled")
            
            # Then run the schema
            schema_path = os.path.join(project_base_dir, "database", "schema.sql")
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Execute schema SQL
                db.session.execute(text(schema_sql))
                db.session.commit()
                print("✓ Database schema initialized successfully")
            else:
                print("⚠️  Schema file not found, skipping schema initialization")
        else:
            print("ℹ️  Using SQLite, skipping pgvector schema initialization")
    except Exception as e:
        print(f"⚠️  Error initializing database schema: {e}")
        # Don't fail the app startup
        pass


def init_documents():
    """Process all PDF documents in rag_docs directory if not already processed"""
    try:
        # Check if we're using PostgreSQL (required for vector operations)
        if 'postgresql' not in db.engine.url.drivername:
            print("ℹ️  Document processing requires PostgreSQL, skipping")
            return
        
        rag_docs_path = os.path.join(project_base_dir, "rag_docs")
        
        if not os.path.exists(rag_docs_path):
            print(f"⚠️  RAG docs directory not found: {rag_docs_path}")
            return
        
        # Find all PDF files in rag_docs directory
        pdf_files = []
        for file in os.listdir(rag_docs_path):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(rag_docs_path, file))
        
        if not pdf_files:
            print("ℹ️  No PDF files found in rag_docs directory")
            return
        
        print(f"📁 Found {len(pdf_files)} PDF file(s) in rag_docs directory")
        
        # Check if documents are already processed
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            
            # Check if document already exists and is completed
            result = db.session.execute(
                text("SELECT id, status FROM documents WHERE filename = :filename"),
                {'filename': filename}
            ).fetchone()
            
            if result and result.status == 'completed':
                print(f"⏭️  Skipping '{filename}' - already processed (ID: {result.id})")
                skipped_count += 1
                continue
                
            try:
                print(f"🔄 Processing document: {filename}")
                
                # Process with local embeddings (no API key required)
                from agents.pdf_processor import process_pdf_file
                doc_id = process_pdf_file(pdf_path, use_local=True)
                
                if doc_id:
                    print(f"✅ Document '{filename}' processed successfully (ID: {doc_id})")
                    processed_count += 1
                else:
                    print(f"⚠️  Document '{filename}' processing returned no ID")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing '{filename}': {e}")
                error_count += 1
        
        # Summary
        print(f"\n📊 Document processing summary:")
        print(f"   ✅ Processed: {processed_count}")
        if skipped_count > 0:
            print(f"   ⏭️  Skipped: {skipped_count}")
        if error_count > 0:
            print(f"   ❌ Errors: {error_count}")
        
    except Exception as e:
        print(f"⚠️  Error during document initialization: {e}")


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)