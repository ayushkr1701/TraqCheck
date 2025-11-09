from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .candidate import Candidate
from .extracted_data import ExtractedData
from .document_request import DocumentRequest
from .submitted_document import SubmittedDocument
