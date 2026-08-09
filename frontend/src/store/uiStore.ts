import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  theme: string;
  workspace: string;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: string) => void;
  setWorkspace: (workspace: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  theme: 'system',
  workspace: 'default',
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => set({ theme }),
  setWorkspace: (workspace) => set({ workspace }),
}));
