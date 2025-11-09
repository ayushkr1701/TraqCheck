import { useState } from 'react';
import { Upload, FileText, Eye } from 'lucide-react';
import { candidateService } from '../../services/candidateService';
import Card from '../shared/Card';
import Badge from '../shared/Badge';
import Button from '../shared/Button';
import DocumentViewer from './DocumentViewer';

export default function DocumentSection({ candidateId, submittedDocuments, onDocumentSubmit }) {
  const [uploading, setUploading] = useState(false);
  const [documentType, setDocumentType] = useState('pan');
  const [viewingDocument, setViewingDocument] = useState(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await candidateService.submitDocuments(candidateId, file, documentType);
      onDocumentSubmit();
      e.target.value = '';
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const getVerificationBadge = (status) => {
    const variants = {
      pending: 'warning',
      verified: 'success',
      rejected: 'error',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  return (
    <Card>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Submitted Documents</h2>

      <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Upload className="w-5 h-5 mr-2 text-blue-600" />
          Upload Identity Documents
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="cursor-pointer">
            <input
              type="file"
              onChange={(e) => {
                setDocumentType('pan');
                handleFileUpload(e);
              }}
              accept=".pdf,.jpg,.jpeg,.png"
              disabled={uploading}
              className="hidden"
            />
            <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-all ${
              uploading && documentType === 'pan'
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50 hover:shadow-md'
            }`}>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mb-3">
                  <FileText className="w-8 h-8 text-white" />
                </div>
                <p className="font-semibold text-gray-900 mb-1">PAN Card</p>
                <p className="text-sm text-gray-600 mb-2">
                  {uploading && documentType === 'pan' ? 'Uploading...' : 'Click to upload'}
                </p>
                <p className="text-xs text-gray-500">PDF, JPG, PNG (max 10MB)</p>
              </div>
            </div>
          </label>

          <label className="cursor-pointer">
            <input
              type="file"
              onChange={(e) => {
                setDocumentType('aadhaar');
                handleFileUpload(e);
              }}
              accept=".pdf,.jpg,.jpeg,.png"
              disabled={uploading}
              className="hidden"
            />
            <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-all ${
              uploading && documentType === 'aadhaar'
                ? 'border-indigo-400 bg-indigo-50'
                : 'border-gray-300 bg-white hover:border-indigo-400 hover:bg-indigo-50 hover:shadow-md'
            }`}>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-full flex items-center justify-center mb-3">
                  <FileText className="w-8 h-8 text-white" />
                </div>
                <p className="font-semibold text-gray-900 mb-1">Aadhaar Card</p>
                <p className="text-sm text-gray-600 mb-2">
                  {uploading && documentType === 'aadhaar' ? 'Uploading...' : 'Click to upload'}
                </p>
                <p className="text-xs text-gray-500">PDF, JPG, PNG (max 10MB)</p>
              </div>
            </div>
          </label>
        </div>

        <div className="mt-4 flex items-start space-x-2 text-xs text-gray-600">
          <svg className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <p>Your documents are securely stored and used only for verification purposes. Ensure images are clear and all details are visible.</p>
        </div>
      </div>

      {submittedDocuments.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <FileText className="w-12 h-12 mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600 font-medium">No documents submitted yet</p>
          <p className="text-sm text-gray-500 mt-1">Upload PAN and Aadhaar cards using the sections above</p>
        </div>
      ) : (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <FileText className="w-4 h-4 mr-2" />
            Uploaded Documents ({submittedDocuments.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {submittedDocuments.map((doc) => (
              <div
                key={doc.id}
                className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                      doc.document_type === 'pan'
                        ? 'bg-blue-100'
                        : 'bg-indigo-100'
                    }`}>
                      <FileText className={`w-6 h-6 ${
                        doc.document_type === 'pan'
                          ? 'text-blue-600'
                          : 'text-indigo-600'
                      }`} />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">
                        {doc.document_type === 'pan' ? 'PAN Card' : 'Aadhaar Card'}
                      </p>
                      {getVerificationBadge(doc.verification_status)}
                    </div>
                  </div>
                </div>
                <div className="mb-3">
                  <p className="text-sm text-gray-600 truncate" title={doc.document_filename}>
                    {doc.document_filename}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Submitted: {new Date(doc.submitted_at).toLocaleDateString()} at {new Date(doc.submitted_at).toLocaleTimeString()}
                  </p>
                </div>
                <Button
                  onClick={() => setViewingDocument(doc)}
                  variant="primary"
                  className="w-full text-sm"
                >
                  <Eye className="w-4 h-4 inline mr-2" />
                  View Document
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {viewingDocument && (
        <DocumentViewer
          document={viewingDocument}
          candidateId={candidateId}
          onClose={() => setViewingDocument(null)}
        />
      )}
    </Card>
  );
}
