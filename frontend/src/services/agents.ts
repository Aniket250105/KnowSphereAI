import api from '@/lib/axios';

export const agentService = {
  chat: async (query: string, agentType: string = 'simple') => {
    const response = await api.post('/agent/chat', { query, agent_type: agentType });
    return response.data;
  },
  runWorkflow: async (query: string) => {
    const response = await api.post('/agent/run', { query });
    return response.data;
  },
  getTools: async () => {
    const response = await api.get('/agent/tools');
    return response.data;
  },
  getHistory: async () => {
    const response = await api.get('/agent/history');
    return response.data;
  }
};
