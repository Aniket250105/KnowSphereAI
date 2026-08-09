import api from '@/lib/axios';

export const chatService = {
  chat: async (query: string, stream: boolean = false) => {
    const url = stream ? '/chat/stream' : '/chat';
    const response = await api.post(url, { query });
    return response.data;
  },
  getHistory: async () => {
    const response = await api.get('/history');
    return response.data;
  }
};
