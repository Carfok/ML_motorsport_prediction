export default function PerformanceDashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-6 bg-slate-900 text-white min-h-screen">
      {/* Header Panel */}
      <div className="col-span-1 md:col-span-2 lg:col-span-4 border-b border-slate-700 pb-4">
        <h1 className="text-3xl font-bold tracking-tight text-blue-400">
          The 2026 Aero-Power Predictor <span className="text-xs text-slate-500 uppercase ml-2 tracking-widest">v2.1</span>
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Deep Neural Inerfence Dashboard for Motorsport Performance.
        </p>
      </div>

      {/* Aerodynamics PINN Data */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">Aero-PINN Metrics</h3>
        <div className="mt-2 flex justify-between items-end">
          <span className="text-2xl font-mono text-emerald-400">0.842</span>
          <span className="text-xs text-slate-400">Cd (Drag)</span>
        </div>
        <div className="mt-2 flex justify-between items-end">
          <span className="text-2xl font-mono text-blue-400">2.518</span>
          <span className="text-xs text-slate-400">Cl (Downforce)</span>
        </div>
      </div>

      {/* Energy TFT Forecasting */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">TFT Energy Map</h3>
        <div className="mt-2 flex justify-between items-end">
          <span className="text-2xl font-mono text-amber-400">12.5%</span>
          <span className="text-xs text-slate-400">SOC at Finish</span>
        </div>
        <div className="mt-2 h-2 w-full bg-slate-700 rounded-full overflow-hidden">
          <div className="h-full bg-amber-500 w-[12%] animate-pulse"></div>
        </div>
      </div>

      {/* GNN Graph Insight */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">GNN Circuit Context</h3>
        <p className="mt-2 text-sm text-slate-300">
          Node Context: <span className="text-blue-400">Curvature R=12m</span>
        </p>
        <p className="text-xs text-slate-500">Predicted Performance: +0.21s Delta</p>
      </div>

      {/* PointNet Ranking */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-lg">
        <h3 className="text-slate-500 text-xs font-semibold uppercase">PointNet Ranking</h3>
        <ol className="mt-2 text-sm space-y-1">
          <li className="flex justify-between"><span className="text-slate-400">1.</span> <span>MAG (FAAS)</span></li>
          <li className="flex justify-between"><span className="text-slate-400">2.</span> <span>ALB (WILL)</span></li>
          <li className="flex justify-between"><span className="text-slate-400">3.</span> <span>NOR (MCLA)</span></li>
        </ol>
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
