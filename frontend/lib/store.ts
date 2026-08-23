import { create } from "zustand";

interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  organization_id: number;
  organization_name?: string;
}

interface AppState {
  user: User | null;
  sidebarOpen: boolean;
  setUser: (user: User | null) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  sidebarOpen: true,
  setUser: (user) => set({ user }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
    set({ user: null });
  },
}));
