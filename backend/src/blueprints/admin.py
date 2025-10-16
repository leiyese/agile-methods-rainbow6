import os
from flask import Blueprint, Response, request, render_template, flash, redirect, url_for, current_app
from database.utils import get_db_connection
from scripts.db_handler import save_chunks, get_all_documents, remove_document
from scripts.legal_chunker import LegalDocumentChunker
from functools import wraps

def check_auth(username, password):
    """Verifierar användarnamn och lösenord"""
    return username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']

def authenticate():
    """Returnerar 401 så att webbläsaren visar inloggningsrutan"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Lägger auth på alla rutter i Blueprinten
@bp.before_request
def before_request():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

def process_pdf_with_chunker(
    pdf_path: str,
    use_local: bool = False,
    chunk_size: int = 300,
    min_chunk: int = 150,
    max_chunk: int = 400,
    overlap: int = 50,
) -> int:
    """Process a PDF using the semantic chunker pipeline from scripts/pdf_chunker.py."""
    chunker = LegalDocumentChunker(
        base_chunk_size=chunk_size,
        min_chunk_size=min_chunk,
        max_chunk_size=max_chunk,
        overlap_size=overlap,
    )
    full_text, _, _ = chunker.extract_text_from_pdf(pdf_path)
    if not full_text.strip():
        raise ValueError(
            "No text could be extracted from the PDF. The file might be scanned or protected."
        )
    chunks = chunker.create_chunks(full_text)
    if not chunks:
        raise ValueError(
            "No semantic chunks were created. The document might lack recognizable sections."
        )
    return save_chunks(pdf_path, chunks, use_local=use_local)

@bp.route('/', methods=['GET'])
def index():
    """Visar uppladdningsformuläret och listan över uppladdade filer"""
    documents = get_all_documents()
    return render_template('admin_index.html', documents=documents)

@bp.route('/upload', methods=['POST'])
def upload():
    """Hanterar PDF-uppladdningar och anropar Semantic Chunker"""
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('admin.index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin.index'))

    if file and file.filename.lower().endswith('.pdf'):
        filename = file.filename
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        use_local = request.form.get('use_local', 'true').lower() == 'true'

        try:
            doc_id = process_pdf_with_chunker(file_path, use_local=use_local)
            if doc_id:
                flash(f'✅ PDF processed successfully! Document ID: {doc_id}')
            else:
                flash('✅ PDF processed successfully! Chunks saved to JSON (no document ID).')
        except Exception as e:
            flash(f'❌ Failed to process PDF: {e}')

        return redirect(url_for('admin.index'))

    flash('Invalid file type')
    return redirect(url_for('admin.index'))


@bp.route('/delete/<int:document_id>', methods=['POST'])
def delete_document(document_id: int):
    """Tar bort angiven PDF"""
    if remove_document(document_id):
        flash('🗑️ Document deleted successfully.')
    else:
        flash('⚠️ Failed to delete document (it may not exist).')
    return redirect(url_for('admin.index'))
