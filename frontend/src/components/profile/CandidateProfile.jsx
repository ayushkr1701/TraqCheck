import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Send } from 'lucide-react';
import { candidateService } from '../../services/candidateService';
import Card from '../shared/Card';
import Badge from '../shared/Badge';
import Button from '../shared/Button';
import Spinner from '../shared/Spinner';
import ConfidenceScore from '../shared/ConfidenceScore';
import DocumentSection from './DocumentSection';

export default function CandidateProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [requestingDocs, setRequestingDocs] = useState(false);
  const [docRequestMessage, setDocRequestMessage] = useState('');

  useEffect(() => {
    loadCandidate();
  }, [id]);

  const loadCandidate = async () => {
    setLoading(true);
    try {
      const data = await candidateService.getCandidate(id);
      setCandidate(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load candidate');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestDocuments = async () => {
    setRequestingDocs(true);
    try {
      const response = await candidateService.requestDocuments(id);
      setDocRequestMessage(response.request_preview);
      await loadCandidate();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to request documents');
    } finally {
      setRequestingDocs(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <p className="text-red-600">Error: {error}</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            Back to Candidates
          </Button>
        </Card>
      </div>
    );
  }

  const { extracted_data, document_requests, submitted_documents } = candidate;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button variant="secondary" onClick={() => navigate('/')} className="mb-6">
        <ArrowLeft className="w-4 h-4 inline mr-2" />
        Back to Candidates
      </Button>

      <div className="space-y-6">
        <Card>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {extracted_data?.full_name?.value || 'Candidate Profile'}
              </h1>
              <p className="text-gray-600 mt-1">{candidate.resume_filename}</p>
              <p className="text-sm text-gray-500 mt-1">
                Uploaded: {new Date(candidate.upload_date).toLocaleString()}
              </p>
            </div>
            <Badge variant={candidate.extraction_status === 'completed' ? 'success' : 'warning'}>
              {candidate.extraction_status}
            </Badge>
          </div>
        </Card>

        {extracted_data && (
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Extracted Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <DataField
                label="Full Name"
                value={extracted_data.full_name?.value}
                confidence={extracted_data.full_name?.confidence}
              />
              <DataField
                label="Email"
                value={extracted_data.email?.value}
                confidence={extracted_data.email?.confidence}
              />
              <DataField
                label="Phone"
                value={extracted_data.phone?.value}
                confidence={extracted_data.phone?.confidence}
              />
              <DataField
                label="Current Company"
                value={extracted_data.current_company?.value}
                confidence={extracted_data.current_company?.confidence}
              />
              <DataField
                label="Designation"
                value={extracted_data.designation?.value}
                confidence={extracted_data.designation?.confidence}
              />
              <DataField
                label="Years of Experience"
                value={extracted_data.years_of_experience}
                confidence={null}
              />
            </div>

            {extracted_data.skills?.value && extracted_data.skills.value.length > 0 && (
              <div className="mt-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Skills
                  <ConfidenceScore confidence={extracted_data.skills?.confidence} />
                </label>
                <div className="flex flex-wrap gap-2">
                  {extracted_data.skills.value.map((skill, index) => (
                    <Badge key={index} variant="info">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {extracted_data.education && (
              <div className="mt-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Education</label>
                <p className="text-gray-900">{extracted_data.education}</p>
              </div>
            )}
          </Card>
        )}

        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Document Request</h2>

          {document_requests && document_requests.length > 0 ? (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900">Latest Request</h3>
                  {document_requests[document_requests.length - 1].request_status === 'auto-generated' && (
                    <Badge variant="info" className="text-xs">
                      Auto-Generated
                    </Badge>
                  )}
                </div>
                <pre className="whitespace-pre-wrap text-sm text-gray-700">
                  {document_requests[document_requests.length - 1].request_message}
                </pre>
                <p className="text-xs text-gray-500 mt-2">
                  Sent: {new Date(document_requests[document_requests.length - 1].requested_at).toLocaleString()}
                </p>
              </div>

              {document_requests.length > 1 && (
                <details>
                  <summary className="cursor-pointer text-blue-600 text-sm">
                    View all requests ({document_requests.length})
                  </summary>
                  <div className="mt-2 space-y-2">
                    {document_requests.slice(0, -1).reverse().map((req) => (
                      <div key={req.id} className="bg-gray-50 p-3 rounded text-sm">
                        <pre className="whitespace-pre-wrap text-gray-700">
                          {req.request_message.substring(0, 200)}...
                        </pre>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(req.requested_at).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          ) : (
            <p className="text-gray-600 mb-4">No document requests sent yet</p>
          )}

          <Button
            onClick={handleRequestDocuments}
            disabled={requestingDocs}
            className="mt-4"
          >
            {requestingDocs ? (
              <>
                <Spinner size="sm" />
                <span className="ml-2">Generating Request...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4 inline mr-2" />
                Request Documents
              </>
            )}
          </Button>
        </Card>

        <DocumentSection
          candidateId={id}
          submittedDocuments={submitted_documents || []}
          onDocumentSubmit={loadCandidate}
        />
      </div>
    </div>
  );
}

function DataField({ label, value, confidence }) {
  return (
    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-1">
        {label}
        {confidence !== null && confidence !== undefined && (
          <span className="ml-2">
            <ConfidenceScore confidence={confidence} />
          </span>
        )}
      </label>
      <p className="text-gray-900">{value || '-'}</p>
    </div>
  );
}
