'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Command } from 'cmdk';
import { MessageSquare, FileText, Bot, BarChart2, CheckCircle, Settings, LogOut } from 'lucide-react';
import { useAuth } from '@/providers/AuthProvider';

export function CommandPalette() {
  const [open, setOpen] = React.useState(false);
  const router = useRouter();
  const { logout } = useAuth();

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-start justify-center pt-[20vh]">
      <Command 
        className="w-full max-w-lg rounded-xl border bg-background shadow-2xl overflow-hidden"
        loop
      >
        <div className="flex items-center border-b px-3">
          <Command.Input 
            autoFocus 
            placeholder="Type a command or search..." 
            className="flex h-12 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>
        <Command.List className="max-h-[300px] overflow-y-auto p-2">
          <Command.Empty className="py-6 text-center text-sm">No results found.</Command.Empty>
          
          <Command.Group heading="Navigation" className="p-1 text-xs font-medium text-muted-foreground">
            <Command.Item onSelect={() => { router.push('/chat'); setOpen(false); }} className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground text-foreground">
              <MessageSquare className="mr-2 h-4 w-4" /> Open Chat
            </Command.Item>
            <Command.Item onSelect={() => { router.push('/documents'); setOpen(false); }} className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground text-foreground">
              <FileText className="mr-2 h-4 w-4" /> Upload Document
            </Command.Item>
            <Command.Item onSelect={() => { router.push('/agents'); setOpen(false); }} className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground text-foreground">
              <Bot className="mr-2 h-4 w-4" /> Run Agent
            </Command.Item>
            <Command.Item onSelect={() => { router.push('/analytics'); setOpen(false); }} className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground text-foreground">
              <BarChart2 className="mr-2 h-4 w-4" /> Analytics
            </Command.Item>
            <Command.Item onSelect={() => { router.push('/evaluation'); setOpen(false); }} className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground text-foreground">
              <CheckCircle className="mr-2 h-4 w-4" /> Evaluation
            </Command.Item>
            <Command.Item onSelect={() => { router.push('/settings'); setOpen(false); }} className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground text-foreground">
              <Settings className="mr-2 h-4 w-4" /> Settings
            </Command.Item>
          </Command.Group>
          
          <Command.Separator className="h-px bg-border my-1" />
          
          <Command.Group heading="Account" className="p-1 text-xs font-medium text-muted-foreground">
            <Command.Item onSelect={() => { logout(); setOpen(false); }} className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground text-foreground">
              <LogOut className="mr-2 h-4 w-4" /> Logout
            </Command.Item>
          </Command.Group>
        </Command.List>
      </Command>
      <div className="fixed inset-0 -z-10" onClick={() => setOpen(false)}></div>
    </div>
  );
}
