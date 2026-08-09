'use client';

import { useAuth } from '@/providers/AuthProvider';
import Link from 'next/link';
import { Bot, FileText, MessageSquare, BarChart2, CheckCircle, Shield } from 'lucide-react';

export default function DashboardHome() {
  const { user } = useAuth();

  return (
    <div className="space-y-8 max-w-5xl mx-auto py-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user?.username}</h1>
        <p className="text-muted-foreground mt-2">
          Here's what's happening in your intelligent knowledge workspace today.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Link href="/chat" className="block group">
          <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 transition-all hover:shadow-md hover:border-primary/50 h-full">
            <div className="flex items-center space-x-4 mb-4">
              <div className="p-3 bg-primary/10 rounded-lg text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <MessageSquare className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold leading-none tracking-tight">Ask KnowSphere</h3>
                <p className="text-sm text-muted-foreground mt-1">Start a new RAG conversation</p>
              </div>
            </div>
          </div>
        </Link>

        <Link href="/documents" className="block group">
          <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 transition-all hover:shadow-md hover:border-primary/50 h-full">
            <div className="flex items-center space-x-4 mb-4">
              <div className="p-3 bg-blue-500/10 rounded-lg text-blue-500 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold leading-none tracking-tight">Documents</h3>
                <p className="text-sm text-muted-foreground mt-1">Upload and manage knowledge</p>
              </div>
            </div>
          </div>
        </Link>

        <Link href="/agents" className="block group">
          <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 transition-all hover:shadow-md hover:border-primary/50 h-full">
            <div className="flex items-center space-x-4 mb-4">
              <div className="p-3 bg-purple-500/10 rounded-lg text-purple-500 group-hover:bg-purple-500 group-hover:text-white transition-colors">
                <Bot className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold leading-none tracking-tight">AI Agents</h3>
                <p className="text-sm text-muted-foreground mt-1">Run complex workflows</p>
              </div>
            </div>
          </div>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg">System Status</h3>
            <Shield className="w-5 h-5 text-green-500" />
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">API Services</span>
              <span className="flex items-center text-green-500"><span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span> Healthy</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Vector Database</span>
              <span className="flex items-center text-green-500"><span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span> Healthy</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">LLM Provider</span>
              <span className="flex items-center text-green-500"><span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span> Connected</span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg">Quick Links</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Link href="/analytics" className="flex items-center p-3 rounded-lg hover:bg-muted transition-colors">
              <BarChart2 className="w-5 h-5 mr-3 text-muted-foreground" />
              <span className="text-sm font-medium">View Analytics</span>
            </Link>
            <Link href="/evaluation" className="flex items-center p-3 rounded-lg hover:bg-muted transition-colors">
              <CheckCircle className="w-5 h-5 mr-3 text-muted-foreground" />
              <span className="text-sm font-medium">Evaluations</span>
            </Link>
            {user?.role === 'ADMIN' && (
              <Link href="/admin" className="flex items-center p-3 rounded-lg hover:bg-muted transition-colors col-span-2">
                <Shield className="w-5 h-5 mr-3 text-muted-foreground" />
                <span className="text-sm font-medium">Admin Dashboard</span>
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
