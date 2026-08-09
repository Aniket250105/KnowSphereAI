'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { evaluationService } from '@/services/evaluation';
import { useAuth } from '@/providers/AuthProvider';
import { Play, CheckCircle, AlertTriangle, Loader2, Trophy, Target, Clock, BookOpen, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function EvaluationPage() {
  const { user } = useAuth();
  const [running, setRunning] = useState(false);
  const [profile, setProfile] = useState('Quick');
  const [runResult, setRunResult] = useState<any>(null);

  const { data: leaderboardData, isLoading, refetch } = useQuery({
    queryKey: ['evaluation-leaderboard'],
    queryFn: evaluationService.getLeaderboard
  });

  const runMutation = useMutation({
    mutationFn: (p: string) => evaluationService.runBenchmark(p),
    onMutate: () => {
      setRunning(true);
      setRunResult(null);
    },
    onSuccess: (data) => {
      setRunResult(data.summary);
      refetch();
    },
    onSettled: () => setRunning(false)
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">RAG Evaluation</h1>
        <p className="text-muted-foreground text-sm">Measure system accuracy, grounding, and retrieval performance.</p>
      </div>

      {user?.role === 'ADMIN' && (
        <div className="border rounded-xl bg-card p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 className="font-semibold text-lg flex items-center">
                <Target className="w-5 h-5 mr-2 text-primary" /> Run Benchmark
              </h3>
              <p className="text-sm text-muted-foreground mt-1">Execute the standard evaluation dataset against the current pipeline.</p>
            </div>
            <div className="flex items-center space-x-3">
              <select 
                value={profile}
                onChange={(e) => setProfile(e.target.value)}
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
                disabled={running}
              >
                <option value="Quick">Quick Profile</option>
                <option value="Comprehensive">Comprehensive Profile</option>
                <option value="Exhaustive">Exhaustive Profile</option>
              </select>
              <button
                onClick={() => runMutation.mutate(profile)}
                disabled={running}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 disabled:opacity-50"
              >
                {running ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                {running ? 'Running...' : 'Execute Run'}
              </button>
            </div>
          </div>

          {runMutation.isError && (
            <div className="mt-4 p-4 rounded-md bg-red-500/10 text-red-500 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Failed to run evaluation. Please check backend logs.
            </div>
          )}

          {runResult && (
            <div className="mt-6 p-4 rounded-lg border bg-muted/30">
              <h4 className="font-medium flex items-center mb-4 text-green-600">
                <CheckCircle className="w-4 h-4 mr-2" /> Run Complete
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-background p-3 rounded-md border">
                  <div className="text-xs text-muted-foreground mb-1">Total Queries</div>
                  <div className="text-xl font-semibold">{runResult.total_queries || 0}</div>
                </div>
                <div className="bg-background p-3 rounded-md border">
                  <div className="text-xs text-muted-foreground mb-1">Avg Grounding</div>
                  <div className="text-xl font-semibold">{((runResult.average_grounding_score || 0) * 100).toFixed(1)}%</div>
                </div>
                <div className="bg-background p-3 rounded-md border">
                  <div className="text-xs text-muted-foreground mb-1">Hallucination Rate</div>
                  <div className="text-xl font-semibold">{((runResult.hallucination_rate || 0) * 100).toFixed(1)}%</div>
                </div>
                <div className="bg-background p-3 rounded-md border">
                  <div className="text-xs text-muted-foreground mb-1">Avg Latency</div>
                  <div className="text-xl font-semibold">{(runResult.average_latency || 0).toFixed(2)}s</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="border rounded-xl bg-card shadow-sm overflow-hidden">
        <div className="p-4 border-b bg-muted/20 flex items-center">
          <Trophy className="w-5 h-5 mr-2 text-yellow-500" />
          <h3 className="font-semibold text-lg">Retrieval Leaderboard</h3>
        </div>
        
        {isLoading ? (
          <div className="p-12 flex justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : leaderboardData?.leaderboard ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground bg-muted/50 uppercase">
                <tr>
                  <th className="px-6 py-3 font-medium">Rank</th>
                  <th className="px-6 py-3 font-medium">Strategy</th>
                  <th className="px-6 py-3 font-medium text-right">Recall@K</th>
                  <th className="px-6 py-3 font-medium text-right">MRR</th>
                  <th className="px-6 py-3 font-medium text-right">Latency (s)</th>
                  <th className="px-6 py-3 font-medium text-right">Score</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {leaderboardData.leaderboard.map((entry: any, index: number) => (
                  <tr key={index} className={cn("hover:bg-muted/30", index === 0 && "bg-yellow-500/5")}>
                    <td className="px-6 py-4 font-medium">
                      <div className="flex items-center">
                        {index === 0 && <span className="w-6 h-6 rounded-full bg-yellow-500 text-white flex items-center justify-center text-xs mr-2">1</span>}
                        {index !== 0 && <span className="text-muted-foreground ml-2 mr-4">{index + 1}</span>}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-medium">{entry.strategy}</td>
                    <td className="px-6 py-4 text-right">{(entry.metrics?.recall_at_k?.toFixed(3)) || '-'}</td>
                    <td className="px-6 py-4 text-right">{(entry.metrics?.mrr?.toFixed(3)) || '-'}</td>
                    <td className="px-6 py-4 text-right">{(entry.metrics?.latency_avg?.toFixed(3)) || '-'}</td>
                    <td className="px-6 py-4 text-right font-semibold text-primary">{entry.score?.toFixed(2) || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-muted-foreground">
            <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No leaderboard data available.</p>
          </div>
        )}
      </div>
    </div>
  );
}
