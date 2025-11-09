from . import db
from datetime import datetime
import uuid

class SubmittedDocument(db.Model):
    __tablename__ = 'submitted_documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False)

    document_type = db.Column(db.String(50), nullable=False)
    document_path = db.Column(db.String(500), nullable=False)
    document_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    verification_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'document_type': self.document_type,
            'document_filename': self.document_filename,
            'file_size': self.file_size,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'verification_status': self.verification_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
