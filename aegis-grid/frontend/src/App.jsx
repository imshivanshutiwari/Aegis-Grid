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

        <aside className="w-96 bg-gray-800 border-l border-gray-700 flex flex-col z-10">
          <div className="p-4 border-b border-gray-700 bg-red-900/20">
            <h2 className="text-lg font-semibold text-red-400 mb-2">CRITICAL THREATS</h2>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {alerts.length === 0 ? <p className="text-gray-500">No active threats.</p> : null}
              {alerts.map((alert, i) => (
                <div key={i} className="bg-gray-900 p-2 rounded border border-red-800 text-sm">
                  {alert.description}
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 flex-1 flex flex-col min-h-0">
            <h2 className="text-lg font-semibold text-blue-400 mb-2">AGENT REASONING LOGS</h2>
            <div className="flex-1 overflow-y-auto space-y-2 text-xs font-mono">
              {logs.length === 0 ? <p className="text-gray-500">Awaiting agent analysis...</p> : null}
              {logs.map((log, i) => (
                <div key={i} className="bg-gray-900 p-2 rounded border border-gray-700 whitespace-pre-wrap">
                  <span className="text-blue-300">[{log.role}]</span> {log.content}
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-gray-700 bg-gray-900">
             <h2 className="text-lg font-semibold text-yellow-500 mb-2">HITL APPROVAL</h2>
             <div className="flex space-x-2">
                <button className="flex-1 bg-green-600 hover:bg-green-500 p-2 rounded flex justify-center items-center space-x-1">
                   <Check size={16} /> <span>EXECUTE</span>
                </button>
                <button className="flex-1 bg-red-600 hover:bg-red-500 p-2 rounded flex justify-center items-center space-x-1">
                   <X size={16} /> <span>ABORT</span>
                </button>
             </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
