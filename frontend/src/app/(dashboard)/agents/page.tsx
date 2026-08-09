'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { agentService } from '@/services/agents';
import { Bot, Play, Wrench, Clock, AlertTriangle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

export default function AgentsPage() {
  const [query, setQuery] = useState('');
  const [agentType, setAgentType] = useState('workflow');
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const { data: toolsData } = useQuery({
    queryKey: ['agent-tools'],
    queryFn: agentService.getTools
  });

  const handleRun = async () => {
    if (!query.trim()) return;
    setRunning(true);
    setResult(null);
    setError('');

    try {
      let res;
      if (agentType === 'workflow') {
        res = await agentService.runWorkflow(query);
      } else {
        res = await agentService.chat(query, agentType);
      }
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute agent workflow');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI Agents</h1>
          <p className="text-muted-foreground text-sm">Run autonomous workflows using configured tools.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="border rounded-xl bg-card p-5">
            <h3 className="font-medium mb-4 flex items-center">
              <Bot className="w-4 h-4 mr-2" /> Configuration
            </h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Agent Type</label>
                <select 
                  value={agentType}
                  onChange={(e) => setAgentType(e.target.value)}
                  className="flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                >
                  <option value="workflow">Workflow Agent</option>
                  <option value="simple">Simple Agent</option>
                  <option value="rag">RAG Agent</option>
                </select>
              </div>

              <div className="pt-4 border-t">
                <h4 className="text-sm font-medium mb-3 flex items-center text-muted-foreground">
                  <Wrench className="w-3 h-3 mr-2" /> Available Tools
                </h4>
                <div className="space-y-2">
                  {toolsData?.tools?.map((tool: any, i: number) => (
                    <div key={i} className="text-xs p-2 rounded bg-muted">
                      <span className="font-semibold block">{tool.name}</span>
                      <span className="text-muted-foreground">{tool.description}</span>
                    </div>
                  )) || <div className="text-xs text-muted-foreground">Loading tools...</div>}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="border rounded-xl bg-card overflow-hidden">
            <div className="p-4 border-b bg-muted/30">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Describe the task you want the agent to perform..."
                className="w-full min-h-[100px] resize-none bg-transparent p-2 text-sm outline-none placeholder:text-muted-foreground"
              />
              <div className="flex justify-between items-center mt-2">
                <span className="text-xs text-muted-foreground">
                  Press Run to start execution.
                </span>
                <button
                  onClick={handleRun}
                  disabled={!query.trim() || running}
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 disabled:opacity-50"
                >
                  {running ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                  {running ? 'Executing...' : 'Run Workflow'}
                </button>
              </div>
            </div>

            <div className="p-6 min-h-[300px] bg-background">
              {!result && !running && !error && (
                <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-12">
                  <Bot className="w-12 h-12 mb-4 opacity-20" />
                  <p>Awaiting instructions</p>
                </div>
              )}

              {running && (
                <div className="flex flex-col items-center justify-center h-full py-12 space-y-4 text-muted-foreground">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  <p className="text-sm animate-pulse">Agent is thinking and using tools...</p>
                </div>
              )}

              {error && (
                <div className="p-4 rounded-md bg-red-500/10 text-red-500 flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Execution Failed</h4>
                    <p className="text-sm mt-1">{error}</p>
                  </div>
                </div>
              )}

              {result && !running && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex items-center justify-between text-xs text-muted-foreground border-b pb-2">
                    <span className="flex items-center"><Bot className="w-3 h-3 mr-1" /> {result.agent_type || 'Workflow'} Agent</span>
                    <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> {result.latency?.toFixed(2)}s</span>
                  </div>
                  
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{result.response}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
