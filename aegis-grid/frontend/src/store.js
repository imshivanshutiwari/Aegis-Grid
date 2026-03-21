import { create } from 'zustand';

export const useStore = create((set) => ({
    units: [],
    alerts: [],
    logs: [],
    gpsJammed: false,
    updateUnits: (newUnits) => set((state) => ({ units: newUnits })),
    addAlert: (alert) => set((state) => ({ alerts: [alert, ...state.alerts] })),
    addLog: (log) => set((state) => ({ logs: [log, ...state.logs] })),
    toggleGpsJamming: () => set((state) => ({ gpsJammed: !state.gpsJammed })),
}));
