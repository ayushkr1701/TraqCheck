import api from './api';

export const candidateService = {
  uploadResume: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/candidates/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });

    return response.data;
  },

  getCandidates: async (page = 1, limit = 10, status = null) => {
    const params = { page, limit };
    if (status) params.status = status;

    const response = await api.get('/candidates', { params });
    return response.data;
  },

  getCandidate: async (candidateId) => {
    const response = await api.get(`/candidates/${candidateId}`);
    return response.data;
  },

  requestDocuments: async (candidateId) => {
    const response = await api.post(`/candidates/${candidateId}/request-documents`);
    return response.data;
  },

  submitDocuments: async (candidateId, file, documentType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    const response = await api.post(`/candidates/${candidateId}/submit-documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
};
