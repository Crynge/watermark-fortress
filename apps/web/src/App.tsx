import { startTransition, useEffect, useMemo, useState } from "react";
import "./App.css";

function resolveApiBase(): string {
  const params = new URLSearchParams(window.location.search);
  return params.get("apiBase") ?? import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8011";
}

const API_BASE = resolveApiBase();

type OverviewPayload = {
  repo_name: string;
  narrative: string;
  attacks: string[];
  benchmark_summary: {
    sample_count: number;
    adaptive_after_mean: number;
    adaptive_healed_mean: number;
    baseline_after_mean: number;
    healing_lift: number;
    fortress_lift_over_baseline: number;
    attack_breakdown: Record<
      string,
      {
        adaptive_after: number;
        adaptive_healed: number;
        baseline_after: number;
      }
    >;
  };
  latest_cases: Array<{
    sample_id: string;
    attack: string;
    adaptive: {
      after_confidence: number;
      healed_confidence: number;
      next_weights: Record<string, number>;
    };
    baseline: {
      after_confidence: number;
    };
  }>;
  example_text: string;
  channel_defaults: Record<string, number>;
};

type BattlePayload = {
  battle: {
    original: {
      text: string;
      manifest: {
        signature_id: string;
        placements: Array<{
          channel: string;
          anchor: string;
          expected_surface: string;
        }>;
      };
    };
    attacked: {
      attack: string;
      text: string;
      checksum: string;
    };
    healed: {
      text: string;
      manifest: {
        signature_id: string;
      };
    };
    detection_before: DetectionSummary;
    detection_after: DetectionSummary;
    detection_healed: DetectionSummary;
    next_weights: Record<string, number>;
  };
};

type DetectionSummary = {
  verdict: string;
  confidence: number;
  matched_placements: number;
  total_placements: number;
  channel_scores: Array<{
    channel: string;
    survival_rate: number;
    matched_count: number;
    expected_count: number;
  }>;
  tamper_flags: string[];
};

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`GET ${path} failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`POST ${path} failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function App() {
  const [overview, setOverview] = useState<OverviewPayload | null>(null);
  const [battleText, setBattleText] = useState("");
  const [selectedAttack, setSelectedAttack] = useState("mixed_pressure");
  const [battle, setBattle] = useState<BattlePayload["battle"] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const nextOverview = await apiGet<OverviewPayload>("/api/overview");
        startTransition(() => {
          setOverview(nextOverview);
          setBattleText(nextOverview.example_text);
          setSelectedAttack(nextOverview.attacks.includes("mixed_pressure") ? "mixed_pressure" : nextOverview.attacks[0]);
        });
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load overview.");
      }
    })();
  }, []);

  useEffect(() => {
    if (!overview) {
      return;
    }
    void runBattle(overview.example_text, selectedAttack);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [overview]);

  async function runBattle(textOverride?: string, attackOverride?: string): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const payload = await apiPost<BattlePayload>("/api/battle", {
        text: textOverride ?? battleText,
        attack: attackOverride ?? selectedAttack,
      });
      startTransition(() => {
        setBattle(payload.battle);
      });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Battle simulation failed.");
    } finally {
      setLoading(false);
    }
  }

  const metrics = useMemo(() => {
    if (!overview) {
      return [];
    }
    return [
      { label: "Adaptive after attack", value: formatConfidence(overview.benchmark_summary.adaptive_after_mean), tone: "copper" },
      { label: "Adaptive after healing", value: formatConfidence(overview.benchmark_summary.adaptive_healed_mean), tone: "emerald" },
      { label: "Static baseline after attack", value: formatConfidence(overview.benchmark_summary.baseline_after_mean), tone: "ice" },
      { label: "Healing lift", value: `+${overview.benchmark_summary.healing_lift.toFixed(3)}`, tone: "amber" },
    ];
  }, [overview]);

  return (
    <div className="shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Adaptive watermarking / red-team benchmark / self-healing provenance mesh</p>
          <h1>Watermark Fortress</h1>
          <p className="hero-body">
            A high-signal benchmark and operations console for testing whether LLM provenance survives character-level
            noise, Unicode scrubbing, punctuation flattening, lexical rewrites, and mixed adversarial pressure.
          </p>
        </div>
        <div className="hero-stats">
          <div className="hero-chip">Python core</div>
          <div className="hero-chip">FastAPI control plane</div>
          <div className="hero-chip">React operator console</div>
          <div className="hero-chip">Benchmark report + PDF</div>
        </div>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <main className="grid">
        <section className="main-column">
          <section className="panel">
            <div className="section-header">
              <span>Mission brief</span>
              <strong>{overview?.repo_name ?? "loading..."}</strong>
            </div>
            <p className="panel-copy">{overview?.narrative ?? "Loading fortress narrative..."}</p>
            <div className="metrics-grid">
              {metrics.map((metric) => (
                <article key={metric.label} className={`metric-card metric-${metric.tone}`}>
                  <span>{metric.label}</span>
                  <strong>{metric.value}</strong>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="section-header">
              <span>Channel controller</span>
              <strong>weighted defense surface</strong>
            </div>
            <div className="weights-grid">
              {Object.entries(overview?.channel_defaults ?? {}).map(([channel, value]) => (
                <article key={channel} className="weight-card">
                  <div className="trace-topline">
                    <strong>{channel}</strong>
                    <span>{value.toFixed(2)}</span>
                  </div>
                  <div className="bar-shell">
                    <div className="bar-fill" style={{ width: `${Math.min(100, value * 52)}%` }} />
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel battlefield-panel">
            <div className="section-header">
              <span>Battlefield</span>
              <strong>{battle?.attacked.attack ?? selectedAttack}</strong>
            </div>
            <div className="battle-controls">
              <textarea
                value={battleText}
                onChange={(event) => setBattleText(event.target.value)}
                placeholder="Paste text to watermark and stress-test..."
              />
              <div className="attack-selector">
                {(overview?.attacks ?? []).map((attack) => (
                  <button
                    key={attack}
                    type="button"
                    className={attack === selectedAttack ? "attack-pill attack-pill-active" : "attack-pill"}
                    onClick={() => setSelectedAttack(attack)}
                  >
                    {attack}
                  </button>
                ))}
              </div>
              <button
                type="button"
                className="primary-action"
                onClick={() => void runBattle()}
                disabled={loading || !battleText.trim()}
              >
                {loading ? "Running..." : "Run Fortress Battle"}
              </button>
            </div>

            <div className="battle-grid">
              <article className="battle-card">
                <span>Original watermark</span>
                <strong>{battle?.original.manifest.signature_id ?? "pending"}</strong>
                <p>{battle?.original.text ?? "Waiting for the first simulation..."}</p>
              </article>
              <article className="battle-card">
                <span>Adversarial rewrite</span>
                <strong>{battle?.attacked.checksum ?? "pending"}</strong>
                <p>{battle?.attacked.text ?? "Attack output will appear here."}</p>
              </article>
              <article className="battle-card">
                <span>Self-healed reissue</span>
                <strong>{battle?.healed.manifest.signature_id ?? "pending"}</strong>
                <p>{battle?.healed.text ?? "Adaptive re-embedding will appear here."}</p>
              </article>
            </div>
          </section>
        </section>

        <aside className="rail">
          <section className="panel">
            <div className="section-header">
              <span>Verdict ladder</span>
              <strong>confidence trace</strong>
            </div>
            <div className="verdict-stack">
              {[
                { label: "Before attack", summary: battle?.detection_before },
                { label: "After attack", summary: battle?.detection_after },
                { label: "After healing", summary: battle?.detection_healed },
              ].map(({ label, summary }) => (
                <article key={label} className="verdict-card">
                  <div className="trace-topline">
                    <strong>{label}</strong>
                    <span>{summary?.verdict ?? "pending"}</span>
                  </div>
                  <p>{summary ? formatConfidence(summary.confidence) : "n/a"}</p>
                  <small>
                    {summary ? `${summary.matched_placements}/${summary.total_placements} placements recovered` : "Awaiting battle run"}
                  </small>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="section-header">
              <span>Attack matrix</span>
              <strong>{overview?.benchmark_summary.sample_count ?? 0} samples</strong>
            </div>
            <div className="matrix-list">
              {Object.entries(overview?.benchmark_summary.attack_breakdown ?? {}).map(([attack, row]) => (
                <article key={attack} className="matrix-card">
                  <div className="trace-topline">
                    <strong>{attack}</strong>
                    <span>{formatConfidence(row.adaptive_healed)}</span>
                  </div>
                  <small>adaptive after {formatConfidence(row.adaptive_after)}</small>
                  <small>baseline after {formatConfidence(row.baseline_after)}</small>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="section-header">
              <span>Channel survival</span>
              <strong>{battle?.detection_after.verdict ?? "pending"}</strong>
            </div>
            <div className="matrix-list">
              {(battle?.detection_after.channel_scores ?? []).map((score) => (
                <article key={score.channel} className="matrix-card">
                  <div className="trace-topline">
                    <strong>{score.channel}</strong>
                    <span>{formatConfidence(score.survival_rate)}</span>
                  </div>
                  <small>{score.matched_count}/{score.expected_count} placements recovered</small>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="section-header">
              <span>Adaptive delta</span>
              <strong>next weights</strong>
            </div>
            <div className="matrix-list">
              {Object.entries(battle?.next_weights ?? {}).map(([channel, value]) => (
                <article key={channel} className="matrix-card">
                  <div className="trace-topline">
                    <strong>{channel}</strong>
                    <span>{value.toFixed(2)}</span>
                  </div>
                  <div className="bar-shell compact-bar">
                    <div className="bar-fill" style={{ width: `${Math.min(100, value * 52)}%` }} />
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="section-header">
              <span>Recent benchmark cases</span>
              <strong>sample ledger</strong>
            </div>
            <div className="case-list">
              {(overview?.latest_cases ?? []).map((item) => (
                <article key={`${item.sample_id}-${item.attack}`} className="case-card">
                  <div className="trace-topline">
                    <strong>{item.sample_id}</strong>
                    <span>{item.attack}</span>
                  </div>
                  <small>adaptive after {formatConfidence(item.adaptive.after_confidence)}</small>
                  <small>adaptive healed {formatConfidence(item.adaptive.healed_confidence)}</small>
                  <small>baseline after {formatConfidence(item.baseline.after_confidence)}</small>
                </article>
              ))}
            </div>
          </section>
        </aside>
      </main>
    </div>
  );
}

export default App;
