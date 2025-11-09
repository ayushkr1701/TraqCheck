from . import db
from datetime import datetime
import uuid

class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_filename = db.Column(db.String(255), nullable=False)
    resume_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    extraction_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    extracted_data = db.relationship('ExtractedData', backref='candidate', uselist=False, cascade='all, delete-orphan')
    document_requests = db.relationship('DocumentRequest', backref='candidate', lazy=True, cascade='all, delete-orphan')
    submitted_documents = db.relationship('SubmittedDocument', backref='candidate', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'resume_filename': self.resume_filename,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'extraction_status': self.extraction_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
