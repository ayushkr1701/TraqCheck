import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react';
import { candidateService } from '../../services/candidateService';
import Card from '../shared/Card';
import Button from '../shared/Button';
import Spinner from '../shared/Spinner';

export default function ResumeUpload() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadProgress(0);
    setError(null);
    setUploadStatus(null);

    try {
      const response = await candidateService.uploadResume(file, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(progress);
      });

      setUploadStatus('success');

      if (response.auto_request_generated) {
        console.log('Autonomous document request generated:', response.auto_request_preview);
      }

      setTimeout(() => {
        navigate(`/candidates/${response.candidate_id}`);
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload resume');
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10485760,
    multiple: false,
  });

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">TraqCheck</h1>
          <p className="text-gray-600">Upload candidate resume to get started</p>
        </div>

        <Card>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />

            {!uploading && uploadStatus !== 'success' && (
              <div>
                <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold mb-2">
                  {isDragActive ? 'Drop the resume here' : 'Drag & drop resume here'}
                </h3>
                <p className="text-gray-500 mb-4">or click to select file</p>
                <p className="text-sm text-gray-400">Supports PDF and DOCX (max 10MB)</p>
              </div>
            )}

            {uploading && (
              <div>
                <Spinner size="lg" />
                <p className="mt-4 text-gray-600">Uploading and processing resume...</p>
                <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="mt-2 text-sm text-gray-500">{uploadProgress}%</p>
              </div>
            )}

            {uploadStatus === 'success' && (
              <div>
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
                <p className="text-lg font-semibold text-green-600">Resume uploaded successfully!</p>
                <p className="text-gray-600 mt-2">Redirecting to candidate profile...</p>
              </div>
            )}

            {uploadStatus === 'error' && (
              <div>
                <XCircle className="w-16 h-16 mx-auto mb-4 text-red-500" />
                <p className="text-lg font-semibold text-red-600">Upload failed</p>
                <p className="text-gray-600 mt-2">{error}</p>
                <Button
                  onClick={() => {
                    setUploadStatus(null);
                    setError(null);
                  }}
                  className="mt-4"
                >
                  Try Again
                </Button>
              </div>
            )}
          </div>

          <div className="mt-6 text-center">
            <Button variant="secondary" onClick={() => navigate('/candidates')}>
              View All Candidates
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
