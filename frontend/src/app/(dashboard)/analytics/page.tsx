'use client';

import { BarChart2, Users, FileText, Activity } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center space-x-3 mb-8">
        <div className="p-3 bg-primary/10 text-primary rounded-xl">
          <BarChart2 className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground text-sm">Monitor usage, engagement, and performance metrics.</p>
        </div>
      </div>

      <div className="border rounded-xl bg-card shadow-sm p-12 text-center text-muted-foreground flex flex-col items-center">
        <Activity className="w-12 h-12 mb-4 opacity-20" />
        <h3 className="font-medium text-foreground mb-2 text-lg">No Analytics Data Available</h3>
        <p className="max-w-md text-sm">
          Analytics endpoints are currently limited in this phase. The UI will be populated once the analytics data pipeline is fully operational.
        </p>
      </div>
    </div>
  );
}
