from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from utils.document_processor import process_document
from workers.celery_app import process_document_task

upload_blueprint = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_blueprint.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to upload documents for processing
    """
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(os.getcwd(), 'uploads')
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Process document asynchronously
            task = process_document_task.delay(file_path)
            
            return jsonify({
                "message": "File uploaded successfully and processing started",
                "filename": filename,
                "task_id": task.id
            }), 200
        else:
            return jsonify({
                "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
