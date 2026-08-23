"use client";
import { useState } from "react";
import { apiFetch, severityColor } from "@/lib/utils";
import { Activity, Search, Globe, Server, Hash, AlertTriangle, Shield } from "lucide-react";

export default function ThreatIntelPage() {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("ip");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const lookup = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await apiFetch(`/api/threat-intel/lookup?type=${type}&query=${encodeURIComponent(query.trim())}`);
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Threat Intelligence</h1>
        <p className="text-sm text-slate-400 mt-1">Investigate IPs, domains, and IOCs</p>
      </div>

      {/* Lookup form */}
      <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <div className="flex flex-col md:flex-row gap-3">
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="ip">IP Address</option>
            <option value="domain">Domain</option>
            <option value="hash">File Hash</option>
            <option value="url">URL</option>
          </select>
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && lookup()}
              placeholder={type === "ip" ? "Enter IP address..." : type === "domain" ? "Enter domain..." : type === "hash" ? "Enter file hash..." : "Enter URL..."}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          <button onClick={lookup} disabled={loading || !query.trim()} className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium disabled:opacity-50">
            {loading ? "Investigating..." : "Investigate"}
          </button>
        </div>
      </div>

      {error && <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      {/* Results */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main info */}
          <div className="lg:col-span-2 space-y-6">
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-4">Indicator Overview</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-xs text-slate-500 mb-1">Indicator</div>
                  <div className="text-sm font-mono text-white">{result.indicator || query}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Type</div>
                  <div className="text-sm text-slate-300 capitalize">{result.type || type}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Reputation</div>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor(result.reputation || "low")}`}>
                    {(result.reputation || "unknown").toUpperCase()}
                  </span>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Risk Score</div>
                  <div className="text-sm text-white">{result.risk_score || 0}/100</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Confidence</div>
                  <div className="text-sm text-white">{result.confidence || 0}%</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Detection Count</div>
                  <div className="text-sm text-white">{result.detection_count || 0}</div>
                </div>
              </div>
            </div>

            {result.geolocation && (
              <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
                <h3 className="text-sm font-semibold text-white mb-3">Geolocation</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-slate-500">Country</div>
                    <div className="text-sm text-slate-300">{result.geolocation.country || "N/A"}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">City</div>
                    <div className="text-sm text-slate-300">{result.geolocation.city || "N/A"}</div>
                  </div>
                </div>
              </div>
            )}

            {result.asn && (
              <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
                <h3 className="text-sm font-semibold text-white mb-3">ASN Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-slate-500">ASN Number</div>
                    <div className="text-sm font-mono text-slate-300">{result.asn.number || "N/A"}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Organization</div>
                    <div className="text-sm text-slate-300">{result.asn.organization || "N/A"}</div>
                  </div>
                </div>
              </div>
            )}

            {result.related_threats?.length > 0 && (
              <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
                <h3 className="text-sm font-semibold text-white mb-3">Related Threats</h3>
                <div className="space-y-2">
                  {result.related_threats.map((threat: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/30">
                      <div>
                        <span className="text-sm text-slate-300">{threat.name}</span>
                        <div className="text-xs text-slate-500">{threat.type}</div>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor(threat.severity)}`}>
                        {threat.severity?.toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-3">Timeline</h3>
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-slate-500">First Seen</div>
                  <div className="text-sm text-slate-300">{result.first_seen ? new Date(result.first_seen).toLocaleDateString() : "N/A"}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500">Last Seen</div>
                  <div className="text-sm text-slate-300">{result.last_seen ? new Date(result.last_seen).toLocaleDateString() : "N/A"}</div>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-3">Risk Assessment</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>Risk Score</span>
                    <span>{result.risk_score || 0}/100</span>
                  </div>
                  <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${(result.risk_score || 0) >= 80 ? "bg-red-500" : (result.risk_score || 0) >= 50 ? "bg-orange-500" : "bg-green-500"}`} style={{ width: `${result.risk_score || 0}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!result && !loading && (
        <div className="text-center py-16 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <Shield className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">Enter an IP, domain, or hash to investigate.</p>
          <p className="text-slate-500 text-sm mt-1">All lookups are performed server-side using threat intelligence feeds.</p>
        </div>
      )}
    </div>
  );
}
