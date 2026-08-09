'use client';

import { useAuth } from '@/providers/AuthProvider';
import { useTheme } from 'next-themes';
import { Settings as SettingsIcon, User, Moon, Sun, Monitor } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function SettingsPage() {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-3 mb-8">
        <div className="p-3 bg-primary/10 text-primary rounded-xl">
          <SettingsIcon className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground text-sm">Manage your profile and application preferences.</p>
        </div>
      </div>

      <div className="space-y-6">
        <div className="border rounded-xl bg-card shadow-sm p-6">
          <h3 className="font-semibold text-lg mb-4 flex items-center">
            <User className="w-5 h-5 mr-2 text-primary" /> Profile
          </h3>
          <div className="space-y-4 max-w-md">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Username</label>
              <div className="mt-1 font-medium">{user?.username}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Email</label>
              <div className="mt-1 font-medium">{user?.email || 'N/A'}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Role</label>
              <div className="mt-1 font-medium">{user?.role}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Organization</label>
              <div className="mt-1 font-medium">{user?.organization}</div>
            </div>
          </div>
        </div>

        <div className="border rounded-xl bg-card shadow-sm p-6">
          <h3 className="font-semibold text-lg mb-4 flex items-center">
            <Monitor className="w-5 h-5 mr-2 text-primary" /> Appearance
          </h3>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">Select your preferred theme for the application.</p>
            {mounted && (
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={() => setTheme('light')}
                  className={`flex items-center space-x-2 px-4 py-2 border rounded-md transition-colors ${theme === 'light' ? 'border-primary bg-primary/5 text-primary' : 'hover:bg-muted'}`}
                >
                  <Sun className="w-4 h-4" />
                  <span>Light</span>
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`flex items-center space-x-2 px-4 py-2 border rounded-md transition-colors ${theme === 'dark' ? 'border-primary bg-primary/5 text-primary' : 'hover:bg-muted'}`}
                >
                  <Moon className="w-4 h-4" />
                  <span>Dark</span>
                </button>
                <button
                  onClick={() => setTheme('system')}
                  className={`flex items-center space-x-2 px-4 py-2 border rounded-md transition-colors ${theme === 'system' ? 'border-primary bg-primary/5 text-primary' : 'hover:bg-muted'}`}
                >
                  <Monitor className="w-4 h-4" />
                  <span>System</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
