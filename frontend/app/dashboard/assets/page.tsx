"use client";
import { useEffect, useState } from "react";
import { apiFetch, formatRelativeTime } from "@/lib/utils";
import { ShieldCheck, Plus, Server, Database, Globe, Wifi, Monitor, X } from "lucide-react";

const typeIcons: Record<string, any> = { server: Server, database: Database, application: Globe, endpoint: Monitor, network_device: Wifi };

export default function AssetsPage() {
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: "", asset_type: "server", ip_address: "", description: "" });

  const fetchAssets = async () => {
    try {
      const data = await apiFetch("/api/assets");
      setAssets(data.assets || data || []);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAssets(); }, []);

  const addAsset = async () => {
    try {
      await apiFetch("/api/assets", { method: "POST", body: JSON.stringify(form) });
      setShowAdd(false);
      setForm({ name: "", asset_type: "server", ip_address: "", description: "" });
      fetchAssets();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const deleteAsset = async (id: number) => {
    if (!confirm("Delete this asset?")) return;
    try {
      await apiFetch(`/api/assets/${id}`, { method: "DELETE" });
      fetchAssets();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Assets</h1>
          <p className="text-sm text-slate-400 mt-1">{assets.length} tracked assets</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm">
          <Plus className="w-4 h-4" />Add Asset
        </button>
      </div>

      {error && <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      {/* Add Modal */}
      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="w-full max-w-md p-6 rounded-2xl border border-slate-800/50 bg-[#0b1120]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Add Asset</h3>
              <button onClick={() => setShowAdd(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-300 mb-1">Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" placeholder="Web Server 01" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Type</label>
                <select value={form.asset_type} onChange={(e) => setForm({ ...form, asset_type: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500">
                  <option value="server">Server</option>
                  <option value="endpoint">Endpoint</option>
                  <option value="database">Database</option>
                  <option value="application">Application</option>
                  <option value="network_device">Network Device</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">IP Address</label>
                <input value={form.ip_address} onChange={(e) => setForm({ ...form, ip_address: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm font-mono focus:outline-none focus:border-blue-500" placeholder="192.168.1.1" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Description</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" placeholder="Main web server" />
              </div>
              <button onClick={addAsset} className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium">Add Asset</button>
            </div>
          </div>
        </div>
      )}

      {/* Assets Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="h-40 rounded-2xl bg-slate-800/30 animate-pulse" />)}
        </div>
      ) : assets.length === 0 ? (
        <div className="text-center py-16 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No assets tracked yet.</p>
          <p className="text-slate-500 text-sm mt-1">Add your first asset to start monitoring.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {assets.map((asset) => {
            const Icon = typeIcons[asset.asset_type] || Server;
            return (
              <div key={asset.id} className="p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30 hover:border-slate-700/50 transition-all group">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                      <Icon className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-white">{asset.name}</h3>
                      <span className="text-xs text-slate-500 capitalize">{asset.asset_type?.replace("_", " ")}</span>
                    </div>
                  </div>
                  <button onClick={() => deleteAsset(asset.id)} className="text-slate-600 hover:text-red-400 text-xs opacity-0 group-hover:opacity-100 transition-all">
                    Delete
                  </button>
                </div>
                {asset.ip_address && (
                  <div className="text-xs font-mono text-slate-400 mb-2">{asset.ip_address}</div>
                )}
                {asset.description && (
                  <p className="text-xs text-slate-500">{asset.description}</p>
                )}
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-slate-800/50">
                  <div className={`w-2 h-2 rounded-full ${asset.status === "active" ? "bg-green-500" : "bg-slate-600"}`} />
                  <span className="text-xs text-slate-500">{asset.status || "active"}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
