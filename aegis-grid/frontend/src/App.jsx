import React, { useEffect, useState } from 'react';
import { useStore } from './store';
import TacticalMap from './components/TacticalMap';
import { ShieldAlert, SignalHigh, Check, X } from 'lucide-react';

export default function App() {
  const { units, alerts, logs, gpsJammed, updateUnits, addAlert, addLog, toggleGpsJamming } = useStore();
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/stream');

    socket.onopen = () => console.log('WebSocket connected');
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.channel === 'units.positions') {
          updateUnits(data.data);
        } else if (data.channel === 'threats.alerts') {
          addAlert(data.data);
        } else if (data.channel === 'agents.reasoning') {
          addLog(data.data);
        }
      } catch (e) {
        console.error("Message parse error:", e)
      }
    };
    socket.onclose = () => console.log('WebSocket disconnected');

    setWs(socket);

    return () => socket.close();
  }, [updateUnits, addAlert, addLog]);

  return (
    <div className="h-screen w-full flex flex-col bg-gray-900 text-white overflow-hidden">
      <header className="flex justify-between items-center p-4 border-b border-gray-700 bg-gray-800 z-10">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="text-red-500" />
          <h1 className="text-xl font-bold uppercase tracking-wider">Aegis-Grid C2</h1>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleGpsJamming}
            className={`px-4 py-2 rounded font-bold ${gpsJammed ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'}`}
          >
            {gpsJammed ? 'GPS JAMMED' : 'Jam GPS'}
          </button>
          <div className="flex items-center space-x-2 text-green-400">
            <SignalHigh />
            <span>LINK-16 ACTIVE</span>
          </div>
        </div>
      </header>

      <div className="flex-1 flex relative">
        <div className="flex-1 relative">
          <TacticalMap />
        </div>

        <aside className="w-96 bg-gray-800 border-l border-gray-700 grid grid-rows-[auto_1fr_auto] h-[calc(100vh-64px)] overflow-hidden z-10">
          <div className="p-4 border-b border-gray-700 bg-red-900/20 overflow-hidden flex flex-col">
            <h2 className="text-lg font-semibold text-red-400 mb-2 flex-shrink-0">CRITICAL THREATS</h2>
            <div className="space-y-2 overflow-y-auto pr-1 custom-scrollbar flex-1 min-h-0">
              {alerts.length === 0 ? <p className="text-gray-500">No active threats.</p> : null}
              {alerts.flat().map((alert, i) => (
                <div key={i} className="bg-gray-900 p-2 rounded border border-red-800 text-sm animate-pulse">
                  {alert.description || 'Hostile activity detected'}
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 flex flex-col min-h-0 overflow-hidden">
            <h2 className="text-lg font-semibold text-blue-400 mb-2 flex-shrink-0">AGENT REASONING LOGS</h2>
            <div className="flex-1 overflow-y-auto space-y-2 text-xs font-mono pr-1 custom-scrollbar">
              {logs.length === 0 ? <p className="text-gray-500">Awaiting agent analysis...</p> : null}
              {logs.map((log, i) => (
                <div key={i} className="bg-gray-900 p-2 rounded border border-gray-700 whitespace-pre-wrap">
                  <span className="text-blue-300">[{log.role}]</span> {log.content}
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-gray-700 bg-gray-900 shadow-2xl">
             <h2 className="text-lg font-semibold text-yellow-500 mb-2">HITL APPROVAL</h2>
             <div className="flex space-x-2">
                <button 
                  onClick={() => ws?.send(JSON.stringify({ command: 'EXECUTE' }))}
                  className="flex-1 bg-green-600 hover:bg-green-500 p-2 rounded flex justify-center items-center space-x-1 transition-all active:scale-95"
                >
                   <Check size={16} /> <span>EXECUTE</span>
                </button>
                <button 
                  onClick={() => ws?.send(JSON.stringify({ command: 'ABORT' }))}
                  className="flex-1 bg-red-600 hover:bg-red-500 p-2 rounded flex justify-center items-center space-x-1 transition-all active:scale-95"
                >
                   <X size={16} /> <span>ABORT</span>
                </button>
             </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
