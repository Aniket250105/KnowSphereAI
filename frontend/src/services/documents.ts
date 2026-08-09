import api from '@/lib/axios';

export const documentService = {
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  getDocuments: async () => {
    const response = await api.get('/documents');
    return response.data;
  },
  deleteDocument: async (id: string) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },
  getDocumentDetails: async (id: string) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  }
};
