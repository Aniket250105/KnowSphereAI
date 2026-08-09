'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useUIStore } from '@/store/uiStore';
import { useAuth } from '@/providers/AuthProvider';
import { cn } from '@/lib/utils';
import {
  MessageSquare,
  FileText,
  Bot,
  BarChart2,
  CheckCircle,
  History,
  Settings,
  Shield,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const navigation = [
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'AI Agents', href: '/agents', icon: Bot },
  { name: 'Analytics', href: '/analytics', icon: BarChart2 },
  { name: 'Evaluation', href: '/evaluation', icon: CheckCircle },
  { name: 'History', href: '/history', icon: History },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Admin', href: '/admin', icon: Shield, adminOnly: true },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, setSidebarOpen } = useUIStore();
  const { user } = useAuth();

  return (
    <div
      className={cn(
        'relative flex flex-col bg-muted/20 border-r transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 border-b">
        {sidebarOpen && <span className="font-bold text-lg">KnowSphere AI</span>}
        {!sidebarOpen && <span className="font-bold text-lg mx-auto">KS</span>}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute -right-3 top-5 rounded-full bg-background border shadow-sm p-1"
        >
          {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      <nav className="flex-1 space-y-1 p-3 overflow-y-auto">
        {navigation.map((item) => {
          if (item.adminOnly && user?.role !== 'ADMIN') return null;
          
          const isActive = pathname.startsWith(item.href);
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                !sidebarOpen && 'justify-center px-0'
              )}
              title={!sidebarOpen ? item.name : undefined}
            >
              <item.icon className={cn('h-5 w-5 flex-shrink-0', sidebarOpen && 'mr-3')} />
              {sidebarOpen && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border mt-auto">
        {sidebarOpen ? (
          <div className="flex flex-col space-y-1">
            <span className="text-sm font-medium truncate">{user?.username || 'User'}</span>
            <span className="text-xs text-muted-foreground truncate">{user?.organization || 'Workspace'}</span>
            <span className="text-[10px] text-muted-foreground pt-2">v0.1.0</span>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xs">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
