"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/utils";
import { Settings as SettingsIcon, User, Building, Key, Bell, Shield, Plus, Trash2, Mail, Send, ExternalLink, CheckCircle, AlertTriangle, Loader2 } from "lucide-react";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [profileForm, setProfileForm] = useState({ full_name: "", email: "" });
  const [saving, setSaving] = useState(false);
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [newKeyName, setNewKeyName] = useState("");

  // Notification settings
  const [notifConfig, setNotifConfig] = useState<any>(null);
  const [notifLoading, setNotifLoading] = useState(false);
  const [notifSaving, setNotifSaving] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testingChannel, setTestingChannel] = useState<string | null>(null);

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      try {
        const u = JSON.parse(userData);
        setUser(u);
        setProfileForm({ full_name: u.full_name || "", email: u.email || "" });
      } catch {}
    }
    setLoading(false);
    fetchApiKeys();
    fetchNotifConfig();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const data = await apiFetch("/api/settings/api-keys");
      setApiKeys(data.keys || data || []);
    } catch {}
  };

  const fetchNotifConfig = async () => {
    setNotifLoading(true);
    try {
      const data = await apiFetch("/api/settings/notifications");
      setNotifConfig(data);
    } catch {
      setNotifConfig({
        email: { enabled: false, smtp_host: "", smtp_port: 587, smtp_user: "", smtp_password: "", from_email: "", to_email: "", use_tls: true },
        slack: { enabled: false, webhook_url: "" },
        custom_webhooks: [],
        severity_filter: { critical: true, high: true, medium: false, low: false },
      });
    } finally {
      setNotifLoading(false);
    }
  };

  const saveProfile = async () => {
    setSaving(true);
    try {
      await apiFetch("/api/settings/profile", { method: "PUT", body: JSON.stringify(profileForm) });
      alert("Profile updated");
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSaving(false);
    }
  };

  const createApiKey = async () => {
    if (!newKeyName.trim()) return;
    try {
      const data = await apiFetch("/api/settings/api-keys", { method: "POST", body: JSON.stringify({ name: newKeyName }) });
      setNewKeyName("");
      fetchApiKeys();
      alert(`API Key created: ${data.key || data.api_key}`);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const deleteApiKey = async (id: number) => {
    if (!confirm("Delete this API key?")) return;
    try {
      await apiFetch(`/api/settings/api-keys/${id}`, { method: "DELETE" });
      fetchApiKeys();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const saveNotifications = async () => {
    setNotifSaving(true);
    try {
      await apiFetch("/api/settings/notifications", { method: "PUT", body: JSON.stringify(notifConfig) });
      alert("Notification settings saved");
    } catch (e: any) {
      alert(e.message);
    } finally {
      setNotifSaving(false);
    }
  };

  const testNotification = async (channel: string) => {
    setTestingChannel(channel);
    setTestResult(null);
    try {
      const body: any = { channel };
      if (channel === "webhook") {
        const wh = notifConfig?.custom_webhooks?.[0];
        if (wh?.url) body.url = wh.url;
        else throw new Error("Add a webhook URL first");
      }
      const result = await apiFetch("/api/settings/notifications/test", { method: "POST", body: JSON.stringify(body) });
      setTestResult({ channel, ...result });
    } catch (e: any) {
      setTestResult({ channel, success: false, error: e.message });
    } finally {
      setTestingChannel(null);
    }
  };

  const addWebhook = () => {
    setNotifConfig((prev: any) => ({
      ...prev,
      custom_webhooks: [...(prev.custom_webhooks || []), { name: "", url: "", enabled: true, headers: {} }],
    }));
  };

  const removeWebhook = (idx: number) => {
    setNotifConfig((prev: any) => ({
      ...prev,
      custom_webhooks: prev.custom_webhooks.filter((_: any, i: number) => i !== idx),
    }));
  };

  const updateWebhook = (idx: number, field: string, value: any) => {
    setNotifConfig((prev: any) => ({
      ...prev,
      custom_webhooks: prev.custom_webhooks.map((wh: any, i: number) => i === idx ? { ...wh, [field]: value } : wh),
    }));
  };

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "organization", label: "Organization", icon: Building },
    { id: "api-keys", label: "API Keys", icon: Key },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "security", label: "Security", icon: Shield },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar tabs */}
        <div className="w-full lg:w-56 flex lg:flex-col gap-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-colors whitespace-nowrap ${activeTab === tab.id ? "bg-purple-600/10 text-purple-400 border border-purple-500/20" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}
            >
              <tab.icon className="w-4 h-4" />{tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === "profile" && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-4">Profile Settings</h3>
              <div className="space-y-4 max-w-lg">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Full Name</label>
                  <input value={profileForm.full_name} onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Email</label>
                  <input value={profileForm.email} onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" disabled />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Role</label>
                  <input value={user?.role || ""} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm" disabled />
                </div>
                <button onClick={saveProfile} disabled={saving} className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium disabled:opacity-50">
                  {saving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </div>
          )}

          {activeTab === "organization" && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-4">Organization</h3>
              <div className="space-y-4 max-w-lg">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Organization Name</label>
                  <input value={user?.organization_name || ""} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm" disabled />
                </div>
                <p className="text-xs text-slate-500">Organization settings are managed by admins.</p>
              </div>
            </div>
          )}

          {activeTab === "api-keys" && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-4">API Keys</h3>
              <div className="flex gap-2 mb-4">
                <input value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="Key name" className="flex-1 px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" />
                <button onClick={createApiKey} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm">
                  <Plus className="w-4 h-4" />Create
                </button>
              </div>
              {apiKeys.length > 0 ? (
                <div className="space-y-2">
                  {apiKeys.map((key) => (
                    <div key={key.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/30">
                      <div>
                        <span className="text-sm text-white">{key.name}</span>
                        <div className="text-xs text-slate-500 font-mono">{key.key_prefix || "••••••••"}</div>
                      </div>
                      <button onClick={() => deleteApiKey(key.id)} className="p-2 text-slate-500 hover:text-red-400">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No API keys created.</p>
              )}
            </div>
          )}

          {activeTab === "notifications" && notifConfig && (
            <div className="space-y-6">
              {/* Severity Filter */}
              <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <Bell className="w-4 h-4 text-purple-400" />Alert Severity Filter
                </h3>
                <p className="text-xs text-slate-500 mb-4">Choose which alert severities trigger external notifications (email, Slack, webhooks).</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { key: "critical", label: "Critical", color: "red" },
                    { key: "high", label: "High", color: "orange" },
                    { key: "medium", label: "Medium", color: "yellow" },
                    { key: "low", label: "Low", color: "green" },
                  ].map((sev) => (
                    <label key={sev.key} className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/30 cursor-pointer hover:bg-slate-800/50 transition-colors">
                      <input
                        type="checkbox"
                        checked={notifConfig.severity_filter?.[sev.key] || false}
                        onChange={(e) => setNotifConfig((prev: any) => ({
                          ...prev,
                          severity_filter: { ...prev.severity_filter, [sev.key]: e.target.checked },
                        }))}
                        className="rounded accent-purple-500"
                      />
                      <span className="text-sm text-slate-300">{sev.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Email Configuration */}
              <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Mail className="w-4 h-4 text-purple-400" />Email Notifications (SMTP)
                  </h3>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifConfig.email?.enabled || false}
                      onChange={(e) => setNotifConfig((prev: any) => ({
                        ...prev,
                        email: { ...prev.email, enabled: e.target.checked },
                      }))}
                      className="rounded accent-purple-500"
                    />
                    <span className="text-xs text-slate-400">{notifConfig.email?.enabled ? "Enabled" : "Disabled"}</span>
                  </label>
                </div>
                {notifConfig.email?.enabled && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">SMTP Host</label>
                      <input value={notifConfig.email?.smtp_host || ""} onChange={(e) => setNotifConfig((prev: any) => ({ ...prev, email: { ...prev.email, smtp_host: e.target.value } }))} className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" placeholder="smtp.gmail.com" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">SMTP Port</label>
                      <input type="number" value={notifConfig.email?.smtp_port || 587} onChange={(e) => setNotifConfig((prev: any) => ({ ...prev, email: { ...prev.email, smtp_port: parseInt(e.target.value) } }))} className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">SMTP Username</label>
                      <input value={notifConfig.email?.smtp_user || ""} onChange={(e) => setNotifConfig((prev: any) => ({ ...prev, email: { ...prev.email, smtp_user: e.target.value } }))} className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" placeholder="your@email.com" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">SMTP Password</label>
                      <input type="password" value={notifConfig.email?.smtp_password || ""} onChange={(e) => setNotifConfig((prev: any) => ({ ...prev, email: { ...prev.email, smtp_password: e.target.value } }))} className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" placeholder="••••••••" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">From Email</label>
                      <input value={notifConfig.email?.from_email || ""} onChange={(e) => setNotifConfig((prev: any) => ({ ...prev, email: { ...prev.email, from_email: e.target.value } }))} className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" placeholder="alerts@yourcompany.com" />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">To Email (Alerts Recipient)</label>
                      <input value={notifConfig.email?.to_email || ""} onChange={(e) => setNotifConfig((prev: any) => ({ ...prev, email: { ...prev.email, to_email: e.target.value } }))} className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" placeholder="soc-team@yourcompany.com" />
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => testNotification("email")}
                        disabled={testingChannel === "email"}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-800/50 text-sm transition-colors disabled:opacity-50"
                      >
                        {testingChannel === "email" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        Send Test Email
                      </button>
                      {testResult?.channel === "email" && (
                        <span className={`flex items-center gap-1 text-xs ${testResult.success ? "text-green-400" : "text-red-400"}`}>
                          {testResult.success ? <><CheckCircle className="w-3 h-3" /> Sent</> : <><AlertTriangle className="w-3 h-3" /> Failed</>}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Slack Configuration */}
              <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <svg className="w-4 h-4 text-purple-400" viewBox="0 0 24 24" fill="currentColor"><path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/></svg>
                    Slack Webhook
                  </h3>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifConfig.slack?.enabled || false}
                      onChange={(e) => setNotifConfig((prev: any) => ({
                        ...prev,
                        slack: { ...prev.slack, enabled: e.target.checked },
                      }))}
                      className="rounded accent-purple-500"
                    />
                    <span className="text-xs text-slate-400">{notifConfig.slack?.enabled ? "Enabled" : "Disabled"}</span>
                  </label>
                </div>
                {notifConfig.slack?.enabled && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Slack Webhook URL</label>
                      <input value={notifConfig.slack?.webhook_url || ""} onChange={(e) => setNotifConfig((prev: any) => ({ ...prev, slack: { ...prev.slack, webhook_url: e.target.value } }))} className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500 font-mono" placeholder="https://hooks.slack.com/services/T00000/B00000/XXXX" />
                      <p className="text-[10px] text-slate-500 mt-1">Create an <a href="https://api.slack.com/messaging/webhooks" target="_blank" rel="noopener" className="text-purple-400 hover:underline">Incoming Webhook</a> in your Slack workspace.</p>
                    </div>
                    <button
                      onClick={() => testNotification("slack")}
                      disabled={testingChannel === "slack"}
                      className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-800/50 text-sm transition-colors disabled:opacity-50"
                    >
                      {testingChannel === "slack" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      Send Test to Slack
                    </button>
                    {testResult?.channel === "slack" && (
                      <span className={`flex items-center gap-1 text-xs ${testResult.success ? "text-green-400" : "text-red-400"}`}>
                        {testResult.success ? <><CheckCircle className="w-3 h-3" /> Sent</> : <><AlertTriangle className="w-3 h-3" /> {testResult.error || "Failed"}</>}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Custom Webhooks */}
              <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <ExternalLink className="w-4 h-4 text-purple-400" />Custom Webhooks
                  </h3>
                  <button onClick={addWebhook} className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-800/50 text-xs transition-colors">
                    <Plus className="w-3 h-3" /> Add Webhook
                  </button>
                </div>
                <p className="text-xs text-slate-500 mb-4">Send alert payloads as JSON POST to any HTTP endpoint (SIEM, SOAR, custom integrations).</p>
                {notifConfig.custom_webhooks?.length > 0 ? (
                  <div className="space-y-3">
                    {notifConfig.custom_webhooks.map((wh: any, idx: number) => (
                      <div key={idx} className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30 space-y-3">
                        <div className="flex items-center gap-3">
                          <input value={wh.name || ""} onChange={(e) => updateWebhook(idx, "name", e.target.value)} className="w-40 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" placeholder="Webhook name" />
                          <input value={wh.url || ""} onChange={(e) => updateWebhook(idx, "url", e.target.value)} className="flex-1 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-white text-sm font-mono focus:outline-none focus:border-purple-500" placeholder="https://your-siem.example.com/webhook" />
                          <label className="flex items-center gap-1 cursor-pointer">
                            <input type="checkbox" checked={wh.enabled} onChange={(e) => updateWebhook(idx, "enabled", e.target.checked)} className="rounded accent-purple-500" />
                            <span className="text-[10px] text-slate-500">On</span>
                          </label>
                          <button onClick={() => removeWebhook(idx)} className="p-2 text-slate-500 hover:text-red-400">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <div className="flex items-center gap-3">
                          <button
                            onClick={() => testNotification("webhook")}
                            disabled={testingChannel === "webhook"}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-800/50 text-xs transition-colors disabled:opacity-50"
                          >
                            {testingChannel === "webhook" ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                            Test
                          </button>
                          {testResult?.channel === "webhook" && (
                            <span className={`flex items-center gap-1 text-xs ${testResult.success ? "text-green-400" : "text-red-400"}`}>
                              {testResult.success ? <><CheckCircle className="w-3 h-3" /> OK</> : <><AlertTriangle className="w-3 h-3" /> {testResult.error || "Failed"}</>}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">No custom webhooks configured.</p>
                )}
              </div>

              {/* Save Button */}
              <div className="flex items-center gap-3">
                <button onClick={saveNotifications} disabled={notifSaving} className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium disabled:opacity-50">
                  {notifSaving ? "Saving..." : "Save Notification Settings"}
                </button>
              </div>
            </div>
          )}

          {activeTab === "security" && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-4">Security Settings</h3>
              <div className="space-y-4 max-w-lg">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Change Password</label>
                  <input type="password" placeholder="Current password" className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500 mb-2" />
                  <input type="password" placeholder="New password" className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500" />
                </div>
                <button className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium">
                  Update Password
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
