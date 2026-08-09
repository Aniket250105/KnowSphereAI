'use client';

import { useQuery } from '@tanstack/react-query';
import { chatService } from '@/services/chat';
import { History as HistoryIcon, Clock, MessageSquare, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function HistoryPage() {
  const { data: historyData, isLoading } = useQuery({
    queryKey: ['agent-history'],
    queryFn: async () => {
      // In a real app we'd fetch both chat history and agent history
      const { agentService } = await import('@/services/agents');
      return await agentService.getHistory();
    }
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-3 mb-8">
        <div className="p-3 bg-primary/10 text-primary rounded-xl">
          <HistoryIcon className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Interaction History</h1>
          <p className="text-muted-foreground text-sm">Review your past conversations and agent workflows.</p>
        </div>
      </div>

      <div className="border rounded-xl bg-card shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-12 flex justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : historyData?.history?.length > 0 ? (
          <div className="divide-y">
            {historyData.history.map((item: any, i: number) => (
              <div key={i} className="p-4 hover:bg-muted/50 transition-colors">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-muted rounded-lg shrink-0 mt-1">
                    <MessageSquare className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{item.query || 'Workflow Execution'}</p>
                    <p className="text-xs text-muted-foreground mt-1 truncate">
                      {item.response || 'No response recorded'}
                    </p>
                    <div className="flex items-center text-xs text-muted-foreground space-x-2 mt-2">
                      <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> {item.timestamp ? formatDistanceToNow(new Date(item.timestamp), { addSuffix: true }) : 'Recently'}</span>
                      {item.latency && <span>• {item.latency.toFixed(2)}s</span>}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center text-muted-foreground flex flex-col items-center">
            <HistoryIcon className="w-12 h-12 mb-4 opacity-20" />
            <p>No history available.</p>
          </div>
        )}
      </div>
    </div>
  );
}
