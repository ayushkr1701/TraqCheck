import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

class FileStorage:
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def save_resume(file):
        if not file:
            raise ValueError("No file provided")

        if not FileStorage.allowed_file(file.filename, Config.ALLOWED_RESUME_EXTENSIONS):
            raise ValueError("Invalid file type. Only PDF and DOCX files are allowed.")

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        resume_folder = os.path.join(Config.UPLOAD_FOLDER, 'resumes')
        os.makedirs(resume_folder, exist_ok=True)

        file_path = os.path.join(resume_folder, unique_filename)
        file.save(file_path)

        return {
            'filename': filename,
            'unique_filename': unique_filename,
            'path': file_path
        }

    @staticmethod
    def save_document(file, document_type):
        if not file:
            raise ValueError("No file provided")

        if not FileStorage.allowed_file(file.filename, Config.ALLOWED_DOCUMENT_EXTENSIONS):
            raise ValueError("Invalid file type. Only PDF and image files are allowed.")

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        documents_folder = os.path.join(Config.UPLOAD_FOLDER, 'documents')
        os.makedirs(documents_folder, exist_ok=True)

        file_path = os.path.join(documents_folder, unique_filename)
        file.save(file_path)

        return {
            'filename': filename,
            'unique_filename': unique_filename,
            'path': file_path,
            'size': os.path.getsize(file_path)
        }

    @staticmethod
    def delete_file(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
        return False
