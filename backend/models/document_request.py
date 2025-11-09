from . import db
from datetime import datetime
import uuid

class DocumentRequest(db.Model):
    __tablename__ = 'document_requests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False)

    request_type = db.Column(db.String(50), nullable=False)
    request_message = db.Column(db.Text, nullable=False)
    request_status = db.Column(db.String(50), default='sent')

    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'request_type': self.request_type,
            'request_message': self.request_message,
            'request_status': self.request_status,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
