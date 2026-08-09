'use client';

import { useQuery } from '@tanstack/react-query';
import { healthService } from '@/services/health';
import { Shield, Server, Database, Activity, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function AdminPage() {
  const { data: health, isLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: healthService.getHealth,
    refetchInterval: 30000,
  });

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return 'text-green-500';
      case 'degraded': return 'text-yellow-500';
      default: return 'text-red-500';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return 'bg-green-500/10';
      case 'degraded': return 'bg-yellow-500/10';
      default: return 'bg-red-500/10';
    }
  };

  const StatusIcon = ({ status }: { status: string }) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'degraded': return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default: return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center space-x-3 mb-8">
        <div className="p-3 bg-primary/10 text-primary rounded-xl">
          <Shield className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground text-sm">System health, users, and infrastructure overview.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="border rounded-xl bg-card shadow-sm overflow-hidden">
          <div className="p-4 border-b bg-muted/20 flex items-center justify-between">
            <h3 className="font-semibold text-lg flex items-center">
              <Activity className="w-5 h-5 mr-2 text-primary" /> System Health
            </h3>
            {isLoading && <span className="text-xs text-muted-foreground animate-pulse">Checking...</span>}
          </div>
          
          <div className="p-0">
            {health ? (
              <div className="divide-y">
                <div className="p-4 flex items-center justify-between hover:bg-muted/30">
                  <div className="flex items-center">
                    <Database className="w-5 h-5 mr-3 text-muted-foreground" />
                    <div>
                      <div className="font-medium">PostgreSQL</div>
                      <div className="text-xs text-muted-foreground">Relational Database</div>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center ${getStatusBg(health.postgres)} ${getStatusColor(health.postgres)}`}>
                    <StatusIcon status={health.postgres} />
                    <span className="ml-1 capitalize">{health.postgres || 'Unknown'}</span>
                  </div>
                </div>
                
                <div className="p-4 flex items-center justify-between hover:bg-muted/30">
                  <div className="flex items-center">
                    <Server className="w-5 h-5 mr-3 text-muted-foreground" />
                    <div>
                      <div className="font-medium">Redis</div>
                      <div className="text-xs text-muted-foreground">Cache & Pub/Sub</div>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center ${getStatusBg(health.redis)} ${getStatusColor(health.redis)}`}>
                    <StatusIcon status={health.redis} />
                    <span className="ml-1 capitalize">{health.redis || 'Unknown'}</span>
                  </div>
                </div>

                <div className="p-4 flex items-center justify-between hover:bg-muted/30">
                  <div className="flex items-center">
                    <Database className="w-5 h-5 mr-3 text-muted-foreground" />
                    <div>
                      <div className="font-medium">Qdrant</div>
                      <div className="text-xs text-muted-foreground">Vector Database</div>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center ${getStatusBg(health.qdrant)} ${getStatusColor(health.qdrant)}`}>
                    <StatusIcon status={health.qdrant} />
                    <span className="ml-1 capitalize">{health.qdrant || 'Unknown'}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 flex flex-col items-center justify-center text-muted-foreground">
                <AlertCircle className="w-8 h-8 mb-2 opacity-50 text-red-500" />
                <p>Health data unavailable.</p>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
           <div className="border rounded-xl bg-card shadow-sm p-6 flex flex-col items-center justify-center h-[200px] text-muted-foreground">
             <Shield className="w-12 h-12 mb-4 opacity-20" />
             <h3 className="font-medium text-foreground mb-1">User Management</h3>
             <p className="text-sm text-center">User management is handled in the backend database directly for this phase.</p>
           </div>
        </div>
      </div>
    </div>
  );
}
