import os
from sqlalchemy import text


def init_documents(db, project_base_dir):
    """Process all PDF documents in rag_docs directory if not already processed"""
    try:
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