from flask import Blueprint, request, jsonify
from models import db, Candidate, ExtractedData, DocumentRequest, SubmittedDocument
from services.file_storage import FileStorage
from services.resume_parser import ResumeParser
from services.langchain_agents import AgentOrchestrator
from services.notification_service import NotificationService
import json

candidates_bp = Blueprint('candidates', __name__)

@candidates_bp.route('/upload', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        file_info = FileStorage.save_resume(file)

        candidate = Candidate(
            resume_filename=file_info['filename'],
            resume_path=file_info['path'],
            extraction_status='processing'
        )
        db.session.add(candidate)
        db.session.commit()

        try:
            print("\n" + "="*80)
            print("LANGCHAIN AGENT ORCHESTRATION STARTED")
            print("="*80)

            resume_text = ResumeParser.parse_resume(file_info['path'])

            orchestrator = AgentOrchestrator()
            result = orchestrator.process_resume_and_request_documents(resume_text)

            normalized_data = result['extracted_data']
            request_message = result['request_message']

            education_value = normalized_data.get('education')
            if isinstance(education_value, dict):
                education_value = education_value.get('value')

            extracted_data = ExtractedData(
                candidate_id=candidate.id,
                full_name=normalized_data['full_name']['value'],
                full_name_confidence=normalized_data['full_name']['confidence'],
                email=normalized_data['email']['value'],
                email_confidence=normalized_data['email']['confidence'],
                phone=normalized_data['phone']['value'],
                phone_confidence=normalized_data['phone']['confidence'],
                current_company=normalized_data['current_company']['value'],
                current_company_confidence=normalized_data['current_company']['confidence'],
                designation=normalized_data['designation']['value'],
                designation_confidence=normalized_data['designation']['confidence'],
                years_of_experience=normalized_data['years_of_experience'],
                education=education_value,
                raw_extracted_data=json.dumps(normalized_data)
            )

            if normalized_data['skills']['value']:
                extracted_data.set_skills_list(normalized_data['skills']['value'])
                extracted_data.skills_confidence = normalized_data['skills']['confidence']

            db.session.add(extracted_data)

            candidate.extraction_status = 'completed'
            db.session.commit()

            auto_request_generated = False
            auto_request_message = None

            try:
                candidate_info = {
                    'full_name': normalized_data['full_name']['value'] or 'Candidate',
                    'email': normalized_data['email']['value'] or '',
                    'phone': normalized_data['phone']['value'] or ''
                }

                document_request = DocumentRequest(
                    candidate_id=candidate.id,
                    request_type='email',
                    request_message=request_message,
                    request_status='auto-generated'
                )

                db.session.add(document_request)
                db.session.commit()

                NotificationService.send_document_request(
                    candidate_email=candidate_info['email'],
                    candidate_phone=candidate_info['phone'],
                    message=request_message
                )

                auto_request_generated = True
                auto_request_message = request_message

                print("\n" + "="*80)
                print("LANGCHAIN ORCHESTRATION COMPLETED SUCCESSFULLY")
                print("="*80 + "\n")
            except Exception as e:
                print(f"Auto-request generation failed: {str(e)}")

            return jsonify({
                'candidate_id': candidate.id,
                'message': 'Resume uploaded and processed successfully',
                'extraction_status': 'completed',
                'auto_request_generated': auto_request_generated,
                'auto_request_preview': auto_request_message[:200] + '...' if auto_request_message else None
            }), 201

        except Exception as e:
            db.session.rollback()
            candidate.extraction_status = 'failed'
            db.session.commit()
            return jsonify({
                'candidate_id': candidate.id,
                'message': f'Resume uploaded but extraction failed: {str(e)}',
                'extraction_status': 'failed'
            }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidates_bp.route('', methods=['GET'])
def list_candidates():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        status = request.args.get('status', None)

        query = Candidate.query

        if status:
            query = query.filter_by(extraction_status=status)

        query = query.order_by(Candidate.upload_date.desc())

        pagination = query.paginate(page=page, per_page=limit, error_out=False)

        candidates_data = []
        for candidate in pagination.items:
            candidate_dict = candidate.to_dict()

            if candidate.extracted_data:
                candidate_dict['name'] = candidate.extracted_data.full_name
                candidate_dict['email'] = candidate.extracted_data.email
                candidate_dict['company'] = candidate.extracted_data.current_company

            candidates_data.append(candidate_dict)

        return jsonify({
            'candidates': candidates_data,
            'total': pagination.total,
            'page': page,
            'limit': limit,
            'pages': pagination.pages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidates_bp.route('/<candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)

        candidate_dict = candidate.to_dict()

        if candidate.extracted_data:
            candidate_dict['extracted_data'] = candidate.extracted_data.to_dict()

        candidate_dict['document_requests'] = [req.to_dict() for req in candidate.document_requests]
        candidate_dict['submitted_documents'] = [doc.to_dict() for doc in candidate.submitted_documents]

        return jsonify(candidate_dict), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidates_bp.route('/<candidate_id>/request-documents', methods=['POST'])
def request_documents(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)

        if not candidate.extracted_data:
            return jsonify({'error': 'No extracted data available for this candidate'}), 400

        extracted_data = candidate.extracted_data

        candidate_info = {
            'full_name': extracted_data.full_name or 'Candidate',
            'email': extracted_data.email or '',
            'phone': extracted_data.phone or '',
            'current_company': extracted_data.current_company or 'our organization',
            'designation': extracted_data.designation or 'the position'
        }

        print("\n[MANUAL REQUEST] Using EmailWriterAgent to generate request...")
        from services.langchain_agents import EmailWriterAgent
        email_writer = EmailWriterAgent()
        request_message = email_writer.generate_document_request_email(candidate_info)

        document_request = DocumentRequest(
            candidate_id=candidate_id,
            request_type='email',
            request_message=request_message,
            request_status='sent'
        )

        db.session.add(document_request)
        db.session.commit()

        return jsonify({
            'request_id': document_request.id,
            'message': 'Document request generated successfully',
            'request_preview': request_message,
            'status': 'sent'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidates_bp.route('/<candidate_id>/submit-documents', methods=['POST'])
def submit_documents(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        document_type = request.form.get('document_type')

        if not document_type or document_type not in ['pan', 'aadhaar']:
            return jsonify({'error': 'Invalid document type. Must be "pan" or "aadhaar"'}), 400

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        file_info = FileStorage.save_document(file, document_type)

        submitted_document = SubmittedDocument(
            candidate_id=candidate_id,
            document_type=document_type,
            document_path=file_info['path'],
            document_filename=file_info['filename'],
            file_size=file_info['size'],
            verification_status='pending'
        )

        db.session.add(submitted_document)
        db.session.commit()

        return jsonify({
            'document_id': submitted_document.id,
            'message': 'Document uploaded successfully',
            'document_type': document_type,
            'verification_status': 'pending'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidates_bp.route('/<candidate_id>/documents/<document_id>', methods=['GET'])
def view_document(candidate_id, document_id):
    from flask import send_file
    import os

    try:
        document = SubmittedDocument.query.filter_by(
            id=document_id,
            candidate_id=candidate_id
        ).first_or_404()

        if not os.path.exists(document.document_path):
            return jsonify({'error': 'Document file not found'}), 404

        return send_file(
            document.document_path,
            as_attachment=False,
            download_name=document.document_filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
