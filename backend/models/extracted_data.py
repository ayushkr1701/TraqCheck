from . import db
from datetime import datetime
import uuid
import json

class ExtractedData(db.Model):
    __tablename__ = 'extracted_data'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False, unique=True)

    full_name = db.Column(db.String(255))
    full_name_confidence = db.Column(db.Float)

    email = db.Column(db.String(255))
    email_confidence = db.Column(db.Float)

    phone = db.Column(db.String(20))
    phone_confidence = db.Column(db.Float)

    current_company = db.Column(db.String(255))
    current_company_confidence = db.Column(db.Float)

    designation = db.Column(db.String(255))
    designation_confidence = db.Column(db.Float)

    skills = db.Column(db.Text)
    skills_confidence = db.Column(db.Float)

    years_of_experience = db.Column(db.Integer)
    education = db.Column(db.Text)

    raw_extracted_data = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_skills_list(self):
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []

    def set_skills_list(self, skills_list):
        self.skills = json.dumps(skills_list)

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'full_name': {
                'value': self.full_name,
                'confidence': self.full_name_confidence
            },
            'email': {
                'value': self.email,
                'confidence': self.email_confidence
            },
            'phone': {
                'value': self.phone,
                'confidence': self.phone_confidence
            },
            'current_company': {
                'value': self.current_company,
                'confidence': self.current_company_confidence
            },
            'designation': {
                'value': self.designation,
                'confidence': self.designation_confidence
            },
            'skills': {
                'value': self.get_skills_list(),
                'confidence': self.skills_confidence
            },
            'years_of_experience': self.years_of_experience,
            'education': self.education,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
