'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function PerformanceDashboard() {
  const [circuit, setCircuit] = useState('madrid-2026');
  const [conditions, setConditions] = useState({
    airTemp: 25,
    trackTemp: 35,
    humidity: 45
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const circuits = [
    { id: 'madrid-2026', name: 'Madrid Street Circuit (IFEMA)' },
    { id: 'monaco-2026', name: 'Circuit de Monaco' },
    { id: 'silverstone-2026', name: 'Silverstone Circuit' },
    { id: 'interlagos-2026', name: 'Autódromo José Carlos Pace' }
  ];

  const runPrediction = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/predict`, {
        circuit_id: circuit,
        driver_id: 14, // Default Fernando Alonso
        air_temperature: parseFloat(conditions.airTemp),
        track_temperature: parseFloat(conditions.trackTemp),
        humidity: parseFloat(conditions.humidity),
        telemetry_window: [] // Empty for now
      });
      setPrediction(response.data);
    } catch (error) {
      console.error("Prediction failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-6 bg-slate-900 text-white min-h-screen">
      {/* Configuration & Selection Panel */}
      <div className="col-span-1 md:col-span-2 lg:col-span-4 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mb-2 flex flex-wrap gap-8 items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-blue-400">
            The 2026 Aero-Power Predictor <span className="text-xs text-slate-500 uppercase ml-2 tracking-widest">v2.1</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Deep Neural Inference Dashboard for Motorsport Performance.
          </p>
        </div>

        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Circuit Selection</label>
            <select 
              value={circuit} 
              onChange={(e) => setCircuit(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-blue-400 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-64 p-2.5 outline-none transition-all"
            >
              {circuits.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-4 p-2.5 bg-slate-900/50 rounded-lg border border-slate-700/30">
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Air Temp (°C)</label>
              <input 
                type="number" 
                value={conditions.airTemp}
                onChange={(e) => setConditions({...conditions, airTemp: e.target.value})}
                className="bg-transparent text-sm text-emerald-400 w-16 outline-none"
              />
            </div>
            <div className="h-8 w-[1px] bg-slate-700 my-auto"></div>
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Track Temp (°C)</label>
              <input 
                type="number" 
                value={conditions.trackTemp}
                onChange={(e) => setConditions({...conditions, trackTemp: e.target.value})}
                className="bg-transparent text-sm text-amber-500 w-16 outline-none"
              />
            </div>
          </div>

          <button 
            onClick={runPrediction}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold uppercase px-6 py-3 rounded-lg transition-colors shadow-lg shadow-blue-900/20 active:translate-y-0.5 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Run Prediction'}
          </button>
        </div>
      </div>

      {/* Aerodynamics PINN Data */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">Aero-PINN Metrics</h3>
        <div className="mt-2 flex justify-between items-end">
          <span className="text-2xl font-mono text-emerald-400">{prediction?.aero_efficiency?.cd || '---'}</span>
          <span className="text-xs text-slate-400">Cd (Drag)</span>
        </div>
        <div className="mt-2 flex justify-between items-end">
          <span className="text-2xl font-mono text-blue-400">{prediction?.aero_efficiency?.cl || '---'}</span>
          <span className="text-xs text-slate-400">Cl (Downforce)</span>
        </div>
      </div>

      {/* Energy TFT Forecasting */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">TFT Energy Map</h3>
        <div className="mt-2 flex justify-between items-end">
          <span className="text-2xl font-mono text-amber-400">{prediction ? `${(prediction.energy_usage.soc_at_finish * 100).toFixed(1)}%` : '---'}</span>
          <span className="text-xs text-slate-400">SOC at Finish</span>
        </div>
        <div className="mt-2 h-2 w-full bg-slate-700 rounded-full overflow-hidden">
          <div 
            className="h-full bg-amber-500 transition-all duration-1000" 
            style={{ width: prediction ? `${prediction.energy_usage.soc_at_finish * 100}%` : '0%' }}
          ></div>
        </div>
      </div>

      {/* GNN Graph Insight */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">GNN Circuit Context</h3>
        <p className="mt-2 text-sm text-slate-300">
          Circuit ID: <span className="text-blue-400">{prediction ? prediction.prediction_id.split('-')[1] : '---'}</span>
        </p>
        <p className="text-xs text-slate-500">Nodes analyzed in GNN graph</p>
      </div>

      {/* PointNet Ranking */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">PointNet Ranking</h3>
        <div className="mt-2 text-sm space-y-1">
          {prediction?.expected_ranking.map((rank, i) => (
            <div key={i} className="flex justify-between">
              <span className="text-slate-400">{i + 1}.</span>
              <span>Driver ID: {rank}</span>
            </div>
          )) || <p className="text-slate-500">No ranking data</p>}
        </div>
      </div>

      {/* 3D Visualizer Placeholder */}
      <div className="col-span-1 md:col-span-2 lg:col-span-4 min-h-[500px] border-2 border-dashed border-slate-800 rounded-xl flex items-center justify-center bg-slate-900/50">
        <div className="text-center p-8 bg-slate-800/30 rounded-2xl backdrop-blur-md border border-white/5 shadow-2xl">
          <p className="text-slate-400 mb-2 font-light">Loading Three.js Circuit Engine...</p>
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
        </div>
      </div>
    </div>
  );
}
