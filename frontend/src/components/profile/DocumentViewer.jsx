import { useState } from 'react';
import { X, Download, ZoomIn } from 'lucide-react';
import Button from '../shared/Button';

export default function DocumentViewer({ document, candidateId, onClose }) {
  const [loading, setLoading] = useState(true);
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';
  const documentUrl = `${apiBaseUrl}/candidates/${candidateId}/documents/${document.id}`;

  const isImage = document.document_filename.match(/\.(jpg|jpeg|png|gif)$/i);
  const isPDF = document.document_filename.match(/\.pdf$/i);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = documentUrl;
    link.download = document.document_filename;
    link.click();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col">
        <div className="flex justify-between items-center p-4 border-b">
          <div>
            <h3 className="text-lg font-semibold">
              {document.document_type === 'pan' ? 'PAN Card' : 'Aadhaar Card'}
            </h3>
            <p className="text-sm text-gray-600">{document.document_filename}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button onClick={handleDownload} variant="secondary" className="text-sm">
              <Download className="w-4 h-4 inline mr-1" />
              Download
            </Button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-4 bg-gray-50">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">Loading document...</div>
            </div>
          )}

          {isImage && (
            <img
              src={documentUrl}
              alt={document.document_filename}
              className="max-w-full h-auto mx-auto"
              onLoad={() => setLoading(false)}
              onError={() => setLoading(false)}
            />
          )}

          {isPDF && (
            <iframe
              src={documentUrl}
              className="w-full h-full min-h-[600px]"
              title={document.document_filename}
              onLoad={() => setLoading(false)}
            />
          )}

          {!isImage && !isPDF && (
            <div className="text-center text-gray-600">
              <p>Preview not available for this file type.</p>
              <Button onClick={handleDownload} className="mt-4">
                Download to View
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
