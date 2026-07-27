/**
 * Gmail inbox triage — per-user OAuth + bucketed messages.
 *
 * Connect a real Gmail account, see inbox sorted into buckets (urgent, promotional,
 * social, updates, normal) based on Gmail's own labels. Refreshes every 15 min
 * while mounted.
 */

import { useEffect, useState } from "react";
import { AlertCircle, Bell, Inbox, Loader2, LogOut, RefreshCw, Tag, Users } from "lucide-react";

import { api, type GmailStatus, type GmailTriage, type GmailMessage } from "../lib/api";
import { Card, Empty } from "../components/ui/primitives";

type BucketName = "urgent" | "promotional" | "social" | "updates" | "normal";

const BUCKET_ICON: Record<BucketName, React.ReactNode> = {
  urgent: <AlertCircle className="w-[16px] h-[16px]" strokeWidth={1.5} />,
  promotional: <Tag className="w-[16px] h-[16px]" strokeWidth={1.5} />,
  social: <Users className="w-[16px] h-[16px]" strokeWidth={1.5} />,
  updates: <Bell className="w-[16px] h-[16px]" strokeWidth={1.5} />,
  normal: <Inbox className="w-[16px] h-[16px]" strokeWidth={1.5} />,
};

const BUCKET_LABEL: Record<BucketName, string> = {
  urgent: "Urgent",
  promotional: "Promotional",
  social: "Social",
  updates: "Updates",
  normal: "Normal",
};

function MessageRow({ msg }: { msg: GmailMessage }) {
  return (
    <div className="flex flex-col gap-1 p-3">
      <div className="flex items-baseline gap-2 min-w-0">
        <div className="text-[13px] font-medium truncate text-foreground">
          {msg.subject || "(no subject)"}
        </div>
        <div className="text-[11px] text-muted-foreground/70 shrink-0">
          {new Date(msg.receivedAt).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          })}
        </div>
      </div>
      <div className="text-[12px] text-muted-foreground/80 truncate">
        {msg.from}
      </div>
      {msg.snippet && (
        <div className="text-[12px] text-muted-foreground/70 line-clamp-2">
          {msg.snippet}
        </div>
      )}
    </div>
  );
}

function BucketSection({
  name,
  messages,
}: {
  name: BucketName;
  messages: GmailMessage[];
}) {
  return (
    <Card className="overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border/50">
        <div className="text-muted-foreground/80">{BUCKET_ICON[name]}</div>
        <div className="text-[13px] font-medium text-foreground flex-1">
          {BUCKET_LABEL[name]}
        </div>
        <div className="text-[11px] font-mono text-muted-foreground/60">
          {messages.length}
        </div>
      </div>
      {messages.length === 0 ? (
        <div className="px-4 py-8 text-center text-[13px] text-muted-foreground/70">
          No messages
        </div>
      ) : (
        <div className="divide-y divide-border/30">
          {messages.slice(0, 5).map((msg) => (
            <MessageRow key={msg.id} msg={msg} />
          ))}
        </div>
      )}
    </Card>
  );
}

export function GmailView() {
  const [status, setStatus] = useState<GmailStatus | null>(null);
  const [triage, setTriage] = useState<GmailTriage | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const s = await api.gmailStatus();
      setStatus(s);
      if (s.linked) {
        const t = await api.gmailTriage();
        setTriage(t);
      }
      setError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load Gmail";
      setError(msg);
      setStatus(null);
      setTriage(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const t = await api.gmailTriage(true);
      setTriage(t);
      setError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Refresh failed";
      setError(msg);
    } finally {
      setRefreshing(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.gmailLogout();
      setStatus(null);
      setTriage(null);
      await fetchStatus();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Logout failed";
      setError(msg);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    if (!status?.linked) return;
    const interval = setInterval(() => {
      api
        .gmailTriage()
        .then(setTriage)
        .catch(() => {});
    }, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, [status?.linked]);

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-4">
      {loading ? (
        <Empty icon={<Loader2 className="w-6 h-6 animate-spin" strokeWidth={1.5} />}>
          Loading…
        </Empty>
      ) : error ? (
        <Empty icon={<AlertCircle className="w-6 h-6 text-muted-foreground/30" strokeWidth={1.5} />}>
          {error}
        </Empty>
      ) : !status?.linked ? (
        <Card className="p-8 flex flex-col items-center gap-4 text-center">
          <div className="text-[14px] font-medium text-foreground">
            Connect your Gmail account
          </div>
          <div className="text-[13px] text-muted-foreground max-w-xs">
            Connect your Google account to see your inbox sorted into buckets: urgent,
            promotional, social, updates, and normal.
          </div>
          <a
            href={api.gmailOauthStart()}
            className="px-3 py-2 bg-primary/10 text-primary text-[13px] font-medium rounded-[6px] hover:bg-primary/15 transition-colors"
          >
            Connect Gmail
          </a>
        </Card>
      ) : triage ? (
        <>
          <Card className="flex items-center justify-between px-4 py-3">
            <div className="text-[13px] text-muted-foreground/80">
              <div className="font-mono text-[12px]">{triage.email}</div>
              <div className="text-[11px]">
                Refreshed{" "}
                {new Date(triage.lastRefreshed).toLocaleTimeString("en-US", {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                })}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-2 rounded-[6px] hover:bg-black/5 dark:hover:bg-white/5 transition-colors disabled:opacity-50"
              >
                <RefreshCw
                  className={`w-[16px] h-[16px] ${refreshing ? "animate-spin" : ""}`}
                  strokeWidth={1.5}
                />
              </button>
              <button
                onClick={handleLogout}
                className="p-2 rounded-[6px] hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
              >
                <LogOut className="w-[16px] h-[16px]" strokeWidth={1.5} />
              </button>
            </div>
          </Card>

          <div className="grid gap-4">
            {(Object.keys(BUCKET_LABEL) as BucketName[]).map((bucket) => (
              <BucketSection
                key={bucket}
                name={bucket}
                messages={triage.buckets[bucket] || []}
              />
            ))}
          </div>
        </>
      ) : (
        <Empty icon={<Loader2 className="w-6 h-6 animate-spin" strokeWidth={1.5} />}>
          Loading inbox…
        </Empty>
      )}
    </div>
  );
}
