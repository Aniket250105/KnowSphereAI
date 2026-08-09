'use client';

import { useAuth } from '@/providers/AuthProvider';
import { useTheme } from 'next-themes';
import { Bell, Search, Sun, Moon, LogOut, User } from 'lucide-react';
import { useEffect, useState } from 'react';

export function TopBar() {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <header className="h-16 border-b bg-background flex items-center justify-between px-4 lg:px-8 shrink-0">
      <div className="flex-1 flex items-center">
        <button className="flex items-center text-muted-foreground bg-muted hover:bg-muted/80 px-4 py-1.5 rounded-md text-sm w-64 justify-between border">
          <span className="flex items-center"><Search className="mr-2 h-4 w-4" /> Search...</span>
          <kbd className="hidden sm:inline-flex items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium opacity-100">
            <span className="text-xs">⌘</span>K
          </kbd>
        </button>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-full hover:bg-muted text-muted-foreground"
        >
          {mounted && theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        
        <button className="p-2 rounded-full hover:bg-muted text-muted-foreground relative">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full"></span>
        </button>

        <div className="h-8 w-px bg-border mx-1"></div>

        <div className="flex items-center gap-3">
          <div className="text-sm text-right hidden md:block">
            <div className="font-medium leading-none">{user?.username}</div>
            <div className="text-xs text-muted-foreground mt-1">{user?.role}</div>
          </div>
          <button className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary relative group">
            <User size={16} />
            <div className="absolute right-0 top-full mt-2 w-48 bg-background border rounded-md shadow-md hidden group-hover:block z-50">
              <div className="p-2">
                <button
                  onClick={logout}
                  className="flex items-center w-full text-left px-2 py-2 text-sm text-red-600 hover:bg-muted rounded-sm"
                >
                  <LogOut size={14} className="mr-2" /> Logout
                </button>
              </div>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
}
