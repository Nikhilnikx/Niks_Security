"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import {
  Bot, Send, X, Trash2, Sparkles, Shield, AlertTriangle, FileWarning,
  Globe, Activity, Zap, Copy, Check, Loader2, Wifi, WifiOff
} from "lucide-react";
import { copilotChat, copilotInvestigateAlert, copilotInvestigateIncident, copilotHealthCheck, copilotClearConversation } from "@/lib/copilot";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface CopilotPanelProps {
  contextType?: string;
  contextId?: number;
}

const QUICK_ACTIONS = [
  { label: "Find Critical Threats", icon: AlertTriangle, message: "What are the most critical threats in our environment right now?", contextType: "dashboard" },
  { label: "Analyze Dashboard", icon: Activity, message: "Summarize the current security posture and highlight the most concerning items.", contextType: "dashboard" },
  { label: "Threat Hunt", icon: Shield, message: "Run a threat hunt across recent logs and alerts. Look for unusual patterns or suspicious activity.", contextType: "threat_hunt" },
  { label: "Find Unusual Activity", icon: Globe, message: "Identify unusual or suspicious activity in our security events. Look for anomalies in login patterns, network traffic, or attack sources." },
];

const CONTEXT_ACTIONS: Record<string, Array<{ label: string; icon: any; message: string; action?: string; contextType?: string }>> = {
  alert: [
    { label: "Investigate with AI", icon: Shield, message: "Investigate this alert thoroughly.", action: "investigate_alert" },
    { label: "Find Related Activity", icon: Globe, message: "Find all related activity from the same source IP.", action: "related" },
    { label: "Explain MITRE", icon: Activity, message: "Explain the MITRE ATT&CK technique associated with this alert.", action: "mitre" },
  ],
  incident: [
    { label: "Analyze Incident", icon: FileWarning, message: "Analyze this incident comprehensively.", action: "investigate_incident" },
    { label: "Summarize Incident", icon: Sparkles, message: "Provide a concise summary of this incident for a management report.", action: "summary" },
    { label: "Recommend Response", icon: Zap, message: "What response actions do you recommend for this incident?", action: "response" },
  ],
  dashboard: [
    { label: "Summarize Dashboard", icon: Activity, message: "What are the most serious threats right now?", contextType: "dashboard" },
    { label: "Find Critical Threats", icon: AlertTriangle, message: "Show me all critical threats that need immediate attention.", contextType: "dashboard" },
  ],
};

export default function CopilotPanel({ contextType, contextId }: CopilotPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copilotStatus, setCopilotStatus] = useState<"online" | "offline" | "checking">("checking");
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Check copilot health on mount and when opened
  useEffect(() => {
    copilotHealthCheck().then((h) => {
      setCopilotStatus(h.status === "online" ? "online" : "offline");
    });
  }, [isOpen]);

  // Listen for Investigate with AI button clicks
  useEffect(() => {
    const handler = (e: CustomEvent) => {
      const { alertId } = e.detail || {};
      if (alertId) {
        setIsOpen(true);
        // Auto-trigger investigation after state update
        setTimeout(() => {
          setLoading(true);
          copilotInvestigateAlert(alertId).then((result) => {
            setMessages([
              { role: "user", content: `Investigate alert #${alertId}`, timestamp: Date.now() },
              { role: "assistant", content: result.response, timestamp: Date.now() },
            ]);
            setLoading(false);
          }).catch(() => setLoading(false));
        }, 500);
      }
    };
    window.addEventListener("copilot-investigate-alert", handler as EventListener);
    return () => window.removeEventListener("copilot-investigate-alert", handler as EventListener);
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async (messageText?: string, ctxType?: string, ctxId?: number) => {
    const text = messageText || input;
    if (!text.trim() || loading) return;

    const userMsg: Message = { role: "user", content: text, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const result = await copilotChat({
        message: text,
        context_type: ctxType || contextType,
        context_id: ctxId || contextId,
      });

      const assistantMsg: Message = {
        role: "assistant",
        content: result.response,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: "⚠️ Failed to reach AI Copilot. Please check that Ollama is running.",
        timestamp: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, contextType, contextId]);

  const handleInvestigate = useCallback(async (action: string) => {
    setLoading(true);
    try {
      let result;
      if (action === "investigate_alert" && contextId) {
        result = await copilotInvestigateAlert(contextId);
      } else if (action === "investigate_incident" && contextId) {
        result = await copilotInvestigateIncident(contextId);
      }
      if (result) {
        setMessages((prev) => [...prev, {
          role: "user",
          content: `[Auto] ${action === "investigate_alert" ? "Investigate alert" : "Investigate incident"} #${contextId}`,
          timestamp: Date.now(),
        }, {
          role: "assistant",
          content: result.response,
          timestamp: Date.now(),
        }]);
      }
    } catch {
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: "⚠️ Investigation failed. Please try again.",
        timestamp: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  }, [contextId]);

  const handleClear = async () => {
    setMessages([]);
    await copilotClearConversation();
  };

  const handleCopy = (idx: number, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMarkdown = (text: string) => {
    // Simple markdown rendering
    let html = text
      .replace(/```[\s\S]*?```/g, (m) => `<pre class="bg-slate-800/50 rounded-lg p-3 text-xs text-slate-300 overflow-x-auto my-2"><code>${m.slice(3, -3)}</code></pre>`)
      .replace(/`([^`]+)`/g, '<code class="bg-slate-800/50 px-1.5 py-0.5 rounded text-purple-300 text-xs">$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
      .replace(/^### (.+)$/gm, '<h3 class="text-sm font-bold text-white mt-4 mb-2 flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-purple-400"></span>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-base font-bold text-white mt-4 mb-2 flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-purple-400"></span>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-lg font-bold text-white mt-4 mb-2">$1</h1>')
      .replace(/^- (.+)$/gm, '<li class="text-slate-300 text-xs ml-4 mb-1 flex items-start gap-2"><span class="text-purple-400 mt-1">•</span><span>$1</span></li>')
      .replace(/^(\d+)\. (.+)$/gm, '<li class="text-slate-300 text-xs ml-4 mb-1 flex items-start gap-2"><span class="text-purple-400 font-semibold">$1.</span><span>$2</span></li>')
      .replace(/\n/g, '<br/>');
    return html;
  };

  const getContextActions = () => {
    if (contextType && CONTEXT_ACTIONS[contextType]) return CONTEXT_ACTIONS[contextType];
    return QUICK_ACTIONS;
  };

  return (
    <>
      {/* Floating button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 group"
        >
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-violet-700 flex items-center justify-center shadow-2xl shadow-purple-500/30 group-hover:shadow-purple-500/50 transition-all group-hover:scale-105">
              <Bot className="w-6 h-6 text-white" />
            </div>
            {copilotStatus === "online" && (
              <div className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-green-400 border-2 border-[#080b16] animate-pulse" />
            )}
          </div>
        </button>
      )}

      {/* Copilot panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-[420px] h-[600px] max-h-[80vh] flex flex-col rounded-2xl border border-slate-700/50 bg-[#0c0f1e]/95 backdrop-blur-xl shadow-2xl shadow-purple-500/10 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/50 bg-gradient-to-r from-purple-900/20 to-transparent">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Security Copilot</h3>
                <div className="flex items-center gap-1.5">
                  {copilotStatus === "online" ? (
                    <>
                      <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                      <span className="text-[10px] text-green-400">Online</span>
                    </>
                  ) : copilotStatus === "offline" ? (
                    <>
                      <div className="w-1.5 h-1.5 rounded-full bg-red-400" />
                      <span className="text-[10px] text-red-400">Offline</span>
                    </>
                  ) : (
                    <span className="text-[10px] text-slate-500">Checking...</span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={handleClear} className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-slate-800/50 transition-colors" title="Clear conversation">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => setIsOpen(false)} className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-slate-800/50 transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-6 px-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-violet-600/20 border border-purple-500/20 flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-purple-400" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white mb-1">How can I help?</h4>
                  <p className="text-xs text-slate-500">I can analyze alerts, investigate incidents, and hunt for threats.</p>
                </div>
                <div className="grid grid-cols-2 gap-2 w-full">
                  {getContextActions().map((action) => (
                    <button
                      key={action.label}
                      onClick={() => {
                        if ("action" in action && action.action && action.action.startsWith("investigate_")) {
                          handleInvestigate(action.action);
                        } else {
                          sendMessage(action.message, "contextType" in action ? action.contextType : contextType);
                        }
                      }}
                      disabled={loading}
                      className="flex items-center gap-2 px-3 py-2.5 rounded-xl bg-slate-800/30 border border-slate-700/30 text-left hover:bg-slate-800/60 hover:border-purple-500/20 transition-all disabled:opacity-50 group"
                    >
                      <action.icon className="w-4 h-4 text-purple-400 group-hover:text-purple-300 flex-shrink-0" />
                      <span className="text-[11px] text-slate-300 group-hover:text-white">{action.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-purple-600/20 border border-purple-500/20 text-white"
                      : "bg-slate-800/30 border border-slate-700/20"
                  }`}>
                    {msg.role === "assistant" && (
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-1.5">
                          <Bot className="w-3.5 h-3.5 text-purple-400" />
                          <span className="text-[10px] text-purple-400 font-medium">Copilot</span>
                        </div>
                        <button
                          onClick={() => handleCopy(idx, msg.content)}
                          className="p-1 rounded text-slate-500 hover:text-white transition-colors"
                        >
                          {copiedIdx === idx ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                        </button>
                      </div>
                    )}
                    <div
                      className="text-xs leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                    />
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-800/30 border border-slate-700/20 rounded-2xl px-4 py-3 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                  <span className="text-xs text-slate-400">Analyzing...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="px-4 py-3 border-t border-slate-800/50">
            <div className="flex items-end gap-2 bg-slate-800/30 border border-slate-700/30 rounded-xl px-3 py-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about alerts, threats, incidents..."
                rows={1}
                className="flex-1 bg-transparent text-sm text-white placeholder-slate-500 resize-none focus:outline-none min-h-[32px] max-h-[100px]"
                style={{ height: "auto" }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = "auto";
                  target.style.height = Math.min(target.scrollHeight, 100) + "px";
                }}
              />
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || loading}
                className="p-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex-shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center justify-between mt-2 px-1">
              <span className="text-[9px] text-slate-600">
                {contextType && contextId ? `Context: ${contextType} #${contextId}` : "No context"}
              </span>
              <span className="text-[9px] text-slate-600">Powered by Ollama</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
