import api from '@/lib/axios';

export const evaluationService = {
  runBenchmark: async (profile: string = 'Quick') => {
    const response = await api.post(`/admin/evaluation/run?profile=${profile}`);
    return response.data;
  },
  getLeaderboard: async () => {
    const response = await api.get('/admin/evaluation/leaderboard/retrieval');
    return response.data;
  }
};
