#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║  GAS Multi-Model Token Usage Tracker                      ║
║  Tests all AI providers — input/output/total + ratings    ║
║  by Muhamad Ridwanjr                                      ║
╚═══════════════════════════════════════════════════════════╝

Usage:
  python3 scripts/gas_token_test.py          # run tests + show dashboard
  python3 scripts/gas_token_test.py --stats  # show saved stats only
  python3 scripts/gas_token_test.py --reset  # reset saved stats
"""

import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
import os
from datetime import datetime
from pathlib import Path

BASE       = Path(__file__).resolve().parent.parent
CONFIG     = BASE / ".gas-agent-config"
USAGE_FILE = BASE / "tasks" / "token_usage.json"

# ── ANSI colors ──────────────────────────────────────────────────────────────
R      = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CORAL  = "\033[38;2;205;95;70m"
AMBER  = "\033[38;2;245;185;85m"
CREAM  = "\033[38;2;245;235;215m"
CYAN   = "\033[38;2;80;220;220m"
GREEN  = "\033[38;2;80;200;120m"
RED    = "\033[38;2;220;80;80m"
YELLOW = "\033[38;2;255;215;0m"
BLUE   = "\033[38;2;100;180;255m"
PURPLE = "\033[38;2;180;120;255m"

# ── Load .gas-agent-config ────────────────────────────────────────────────────
def load_config() -> dict:
    cfg = {}
    if CONFIG.exists():
        for line in CONFIG.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                cfg[k.strip()] = v.strip()
    return cfg

# ── Model definitions ─────────────────────────────────────────────────────────
# Each entry describes how to call the API and metadata for display.
def get_models(cfg: dict) -> list:
    OR_KEY   = cfg.get("OPENROUTER_API_KEY", "")
    KIMI_KEY = cfg.get("KIMI_API_KEY", "")
    GEM_KEY  = cfg.get("GEMINI_API_KEY", "")
    VTX_KEY  = cfg.get("VERTEX_API_KEY", "")
    VTX_PRJ  = cfg.get("VERTEX_PROJECT", "gen-lang-client-0060492434")

    return [
        # ── 1. Claude Code · CLI subprocess ──────────────────────────────────
        {
            "id":       "claude-primary",
            "label":    "Claude Code  [Primary · CLI]",
            "color":    CORAL,
            "provider": "claude_cli",
            "rating":   5.0,
        },

        # ── 2. Kimi k2.5 · Moonshot Direct ───────────────────────────────────
        {
            "id":       "kimi-2.5-direct",
            "label":    "Kimi k2.5  [Moonshot Direct]",
            "color":    CYAN,
            "provider": "openai_compat",
            "base_url": "https://api.moonshot.ai/v1",
            "model":    "kimi-k2.5",
            "fallback": "moonshot-v1-32k",
            "api_key":  KIMI_KEY,
            "rating":   4.5,
        },

        # ── 3. Gemini 2.5 Flash · Google AI Studio ────────────────────────────
        {
            "id":       "gemini-studio",
            "label":    "Gemini 2.5 Flash  [Google AI Studio]",
            "color":    BLUE,
            "provider": "gemini_studio",
            "model":    "gemini-2.5-flash-lite-preview-06-17",
            "fallback": "gemini-2.0-flash",
            "api_key":  GEM_KEY,
            "rating":   4.5,
        },

        # ── 4. Gemini · Vertex AI ─────────────────────────────────────────────
        {
            "id":       "gemini-vertex",
            "label":    "Gemini 2.5 Flash  [Vertex AI]",
            "color":    PURPLE,
            "provider": "gemini_vertex",
            "model":    "gemini-2.5-flash",
            "api_key":  VTX_KEY,
            "project":  VTX_PRJ,
            "rating":   4.5,
        },

        # ── 5. DeepSeek V3.2 · OpenRouter ────────────────────────────────────
        {
            "id":       "deepseek-v3.2-or",
            "label":    "DeepSeek V3.2  [OpenRouter]",
            "color":    GREEN,
            "provider": "openrouter",
            "model":    "deepseek/deepseek-v3.2",
            "fallback": "deepseek/deepseek-chat-v3-0324",
            "api_key":  OR_KEY,
            "rating":   4.0,
        },

        # ── 6. DeepSeek R1 · OpenRouter ───────────────────────────────────────
        {
            "id":       "deepseek-r1-or",
            "label":    "DeepSeek R1  [OpenRouter]",
            "color":    GREEN,
            "provider": "openrouter",
            "model":    "deepseek/deepseek-r1-0528",
            "fallback": "deepseek/deepseek-r1",
            "api_key":  OR_KEY,
            "rating":   4.5,
        },

        # ── 7. Grok · OpenRouter ──────────────────────────────────────────────
        {
            "id":       "grok-or",
            "label":    "Grok 4.20 Multi-Agent  [OpenRouter]",
            "color":    AMBER,
            "provider": "openrouter",
            "model":    "x-ai/grok-4.20-multi-agent-beta",
            "fallback": "x-ai/grok-3-beta",
            "api_key":  OR_KEY,
            "rating":   4.5,
        },

        # ── 8. Gemini 3.1 Flash Lite · OpenRouter (separate from AI Studio) ───
        {
            "id":       "gemini-lite-or",
            "label":    "Gemini 3.1 Flash Lite  [OpenRouter]",
            "color":    YELLOW,
            "provider": "openrouter",
            "model":    "google/gemini-3.1-flash-lite-preview",
            "fallback": "google/gemini-2.5-flash-lite",
            "api_key":  OR_KEY,
            "rating":   4.0,
        },
    ]

# ── HTTP helper (no dependencies — pure stdlib) ───────────────────────────────
def post_json(url: str, headers: dict, body: dict, timeout: int = 30) -> tuple:
    """Returns (response_dict, latency_s, error_str)."""
    data = json.dumps(body).encode()
    req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
    t0   = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            lat = round(time.time() - t0, 2)
            return json.loads(resp.read()), lat, None
    except urllib.error.HTTPError as e:
        lat = round(time.time() - t0, 2)
        body_err = e.read().decode(errors="replace")
        return None, lat, f"HTTP {e.code}: {body_err[:200]}"
    except Exception as e:
        lat = round(time.time() - t0, 2)
        return None, lat, str(e)[:200]

TEST_PROMPT = "Reply with exactly one word: OK"

# ── Provider-specific callers ─────────────────────────────────────────────────

def call_claude_cli(model_cfg: dict) -> dict:
    """Run claude -p via subprocess, parse JSON output for token usage."""
    try:
        t0  = time.time()
        out = subprocess.run(
            ["claude", "-p", TEST_PROMPT, "--output-format", "json"],
            capture_output=True, text=True, timeout=60
        )
        lat = round(time.time() - t0, 2)
        if out.returncode != 0:
            err = (out.stderr or out.stdout or "exit code " + str(out.returncode))[:200]
            return {"error": err, "latency": lat}
        data    = json.loads(out.stdout)
        usage   = data.get("usage", {})
        inp     = usage.get("input_tokens", 0)
        cache_r = usage.get("cache_read_input_tokens", 0)
        cache_c = usage.get("cache_creation_input_tokens", 0)
        outp    = usage.get("output_tokens", 0)
        total   = inp + cache_r + cache_c + outp
        cost    = data.get("total_cost_usd", 0.0)
        model_u = list(data.get("modelUsage", {}).keys())
        return {
            "input":    inp + cache_r + cache_c,   # prompt + cache = total input
            "output":   outp,
            "total":    total,
            "latency":  lat,
            "cost_usd": cost,
            "response": (data.get("result") or "")[:80],
            "_model_used": model_u[0] if model_u else "claude",
            "_cache_read": cache_r,
            "_cache_create": cache_c,
        }
    except FileNotFoundError:
        return {"error": "claude CLI not found in PATH", "latency": 0}
    except subprocess.TimeoutExpired:
        return {"error": "claude CLI timed out (60s)", "latency": 60}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "latency": 0}
    except Exception as e:
        return {"error": str(e)[:200], "latency": 0}


def call_openai_compat(model_cfg: dict) -> dict:
    key  = model_cfg.get("api_key", "")
    base = model_cfg.get("base_url", "https://openrouter.ai/api/v1")
    if not key:
        return {"error": "API key not set"}

    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {key}",
        "HTTP-Referer":  "https://gasstrategyai.com",
        "X-Title":       "GAS Token Tracker",
        "User-Agent":    "GAS-TokenTracker/1.0",
    }
    body = {
        "model": model_cfg["model"],
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        "max_tokens": 20,
        # no temperature — reasoning models (kimi-k2.5, deepseek-r1) only accept temp=1
    }
    result, lat, err = post_json(f"{base}/chat/completions", headers, body)

    if err:
        # try fallback model if available
        fallback = model_cfg.get("fallback")
        if fallback and fallback != model_cfg["model"]:
            body["model"] = fallback
            result, lat, err = post_json(f"{base}/chat/completions", headers, body)
            if result:
                model_cfg["_used_fallback"] = fallback

    if err:
        return {"error": err, "latency": lat}

    usage   = result.get("usage") or {}
    choices = result.get("choices") or [{}]
    choice  = choices[0] if choices else {}
    message = choice.get("message") or {} if isinstance(choice, dict) else {}
    if isinstance(message, dict):
        # Kimi k2.5 is a reasoning model — uses reasoning_content, content may be empty
        content = (message.get("content") or message.get("reasoning_content") or "")[:80]
    else:
        content = ""
    return {
        "input":    usage.get("prompt_tokens", 0),
        "output":   usage.get("completion_tokens", 0),
        "total":    usage.get("total_tokens", 0),
        "latency":  lat,
        "response": content,
    }


def call_gemini_studio(model_cfg: dict) -> dict:
    key   = model_cfg.get("api_key", "")
    model = model_cfg.get("model", "gemini-2.0-flash")
    if not key:
        return {"error": "GEMINI_API_KEY not set"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"role": "user", "parts": [{"text": TEST_PROMPT}]}],
        "generationConfig": {"maxOutputTokens": 20},
    }
    result, lat, err = post_json(url, headers, body)

    if err:
        fallback = model_cfg.get("fallback")
        if fallback and fallback != model:
            url2 = f"https://generativelanguage.googleapis.com/v1beta/models/{fallback}:generateContent?key={key}"
            result, lat, err = post_json(url2, headers, body)
            if result:
                model_cfg["_used_fallback"] = fallback

    if err:
        return {"error": err, "latency": lat}

    meta  = result.get("usageMetadata", {})
    parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
    resp  = parts[0].get("text", "")[:80] if parts else ""
    return {
        "input":   meta.get("promptTokenCount", 0),
        "output":  meta.get("candidatesTokenCount", 0),
        "total":   meta.get("totalTokenCount", 0),
        "latency": lat,
        "response": resp,
    }


def call_gemini_vertex(model_cfg: dict) -> dict:
    key     = model_cfg.get("api_key", "")
    model   = model_cfg.get("model", "gemini-2.5-flash")
    project = model_cfg.get("project", "gen-lang-client-0060492434")
    if not key:
        return {"error": "VERTEX_API_KEY not set"}

    body = {
        "contents": [{"role": "user", "parts": [{"text": TEST_PROMPT}]}],
        "generationConfig": {"maxOutputTokens": 20},
    }

    # Attempt 1: Vertex AI with project ID + API key param
    url1 = (
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/"
        f"locations/us-central1/publishers/google/models/{model}:generateContent"
        f"?key={key}"
    )
    result, lat, err = post_json(url1, {"Content-Type": "application/json"}, body)

    # Attempt 2: Vertex AI with project ID + Bearer token
    if err:
        url2 = (
            f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/"
            f"locations/us-central1/publishers/google/models/{model}:generateContent"
        )
        result, lat, err = post_json(
            url2,
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            body,
        )

    # Attempt 3: aiplatform publishers endpoint (no project) + Bearer
    if err:
        url3 = (
            f"https://aiplatform.googleapis.com/v1beta1/publishers/google/"
            f"models/{model}:generateContent"
        )
        result, lat, err = post_json(
            url3,
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            body,
        )

    if err:
        return {"error": err, "latency": lat}

    meta  = result.get("usageMetadata", {})
    parts = (result.get("candidates") or [{}])[0]
    parts = parts.get("content", {}).get("parts", [{}]) if isinstance(parts, dict) else [{}]
    resp  = parts[0].get("text", "")[:80] if parts else ""
    return {
        "input":   meta.get("promptTokenCount", 0),
        "output":  meta.get("candidatesTokenCount", 0),
        "total":   meta.get("totalTokenCount", 0),
        "latency": lat,
        "response": resp,
    }


def run_model(model_cfg: dict) -> dict:
    provider = model_cfg.get("provider", "openai_compat")
    if provider == "claude_cli":
        return call_claude_cli(model_cfg)
    elif provider in ("openai_compat", "openrouter"):
        return call_openai_compat(model_cfg)
    elif provider == "gemini_studio":
        return call_gemini_studio(model_cfg)
    elif provider == "gemini_vertex":
        return call_gemini_vertex(model_cfg)
    return {"error": "unknown provider"}


# ── Persistence ───────────────────────────────────────────────────────────────
def load_usage() -> dict:
    if USAGE_FILE.exists():
        try:
            return json.loads(USAGE_FILE.read_text())
        except Exception:
            pass
    return {"models": {}, "last_run": None, "total_runs": 0}


def save_usage(data: dict):
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2))


def accumulate(usage: dict, model_id: str, result: dict):
    if model_id not in usage["models"]:
        usage["models"][model_id] = {
            "runs": 0, "errors": 0,
            "input_total": 0, "output_total": 0, "token_total": 0,
            "latency_total": 0.0,
        }
    m = usage["models"][model_id]
    if "error" in result:
        m["errors"] += 1
    else:
        m["runs"]          += 1
        m["input_total"]   += result.get("input", 0)
        m["output_total"]  += result.get("output", 0)
        m["token_total"]   += result.get("total", 0)
        m["latency_total"] += result.get("latency", 0.0)


# ── Display helpers ───────────────────────────────────────────────────────────
def stars(rating: float) -> str:
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


def rating_color(rating: float) -> str:
    if rating >= 4.8: return GREEN
    if rating >= 4.0: return CYAN
    if rating >= 3.0: return AMBER
    return RED


def fmt_num(n: int) -> str:
    return f"{n:,}"


def bar(n: int, max_n: int, width: int = 12) -> str:
    if max_n == 0:
        return "─" * width
    filled = round(n / max_n * width)
    return "█" * filled + "░" * (width - filled)


# ── Dashboard ─────────────────────────────────────────────────────────────────
def show_dashboard(models: list, results: dict | None, usage: dict):
    print()
    print(f"{CORAL}  ╔══════════════════════════════════════════════════════════════════╗{R}")
    print(f"{CORAL}  ║{R}  {BOLD}{CREAM}GAS · Multi-Model Token Usage Tracker{R}                        {CORAL}║{R}")
    print(f"{CORAL}  ╠══════════════════════════════════════════════════════════════════╣{R}")
    ts = usage.get("last_run", "never")
    runs = usage.get("total_runs", 0)
    print(f"{CORAL}  ║{R}  {DIM}Last run: {ts}   Total test runs: {runs}{R}".ljust(73) + f"{CORAL}║{R}")
    print(f"{CORAL}  ╚══════════════════════════════════════════════════════════════════╝{R}")
    print()

    # header row
    print(f"  {BOLD}{'MODEL':<42} {'INPUT':>8} {'OUTPUT':>8} {'TOTAL':>8}  {'LATENCY':>8}  {'RATING'}{R}")
    print(f"  {CORAL}{'─'*42} {'─'*8} {'─'*8} {'─'*8}  {'─'*8}  {'─'*14}{R}")

    grand_input  = 0
    grand_output = 0
    grand_total  = 0

    for m in models:
        mid   = m["id"]
        color = m.get("color", CREAM)
        label = m["label"]
        rating= m.get("rating", 4.0)
        rc    = rating_color(rating)
        star  = stars(rating)

        if m.get("skip"):  # legacy guard — no longer used
            print(f"  {color}{label:<42}{R}  {DIM}{'—':>7} {'—':>8} {'—':>8}  {'CLI':>8}{R}  {rc}{star}{R}")
            continue

        # Aggregate from saved usage
        saved = usage["models"].get(mid, {})
        s_in  = saved.get("input_total", 0)
        s_out = saved.get("output_total", 0)
        s_tot = saved.get("token_total", 0)
        s_runs= saved.get("runs", 0)
        s_err = saved.get("errors", 0)
        s_lat = saved.get("latency_total", 0.0)
        avg_lat = round(s_lat / s_runs, 2) if s_runs > 0 else 0.0

        # Current test result (if just ran)
        cur = (results or {}).get(mid)
        if cur and "error" not in cur:
            row_in  = fmt_num(s_in)
            row_out = fmt_num(s_out)
            row_tot = fmt_num(s_tot)
            row_lat = f"{avg_lat:.2f}s" if avg_lat else "—"
            status  = f"{GREEN}✅{R}"
            resp_preview = cur.get("response", "")[:30]
        elif cur and "error" in cur:
            row_in = row_out = row_tot = "ERR"
            row_lat = f"{cur.get('latency', 0):.2f}s"
            status  = f"{RED}✗{R}"
            resp_preview = cur["error"][:50]
        elif s_runs > 0:
            row_in  = fmt_num(s_in)
            row_out = fmt_num(s_out)
            row_tot = fmt_num(s_tot)
            row_lat = f"{avg_lat:.2f}s" if avg_lat else "—"
            status  = f"{DIM}~{R}"
            resp_preview = ""
        else:
            row_in = row_out = row_tot = "—"
            row_lat = "—"
            status  = f"{DIM}?{R}"
            resp_preview = "not tested"

        grand_input  += s_in
        grand_output += s_out
        grand_total  += s_tot

        extra_notes = []
        if cur and cur.get("_used_fallback"):
            extra_notes.append(f"{DIM}fallback: {cur['_used_fallback']}{R}")
        if cur and cur.get("cost_usd"):
            extra_notes.append(f"{YELLOW}${cur['cost_usd']:.5f}{R}")
        if cur and cur.get("_model_used"):
            extra_notes.append(f"{DIM}{cur['_model_used']}{R}")
        notes_str = "  " + "  ".join(extra_notes) if extra_notes else ""

        print(
            f"  {status} {color}{label:<40}{R}"
            f"  {CYAN}{row_in:>7}{R}"
            f"  {GREEN}{row_out:>7}{R}"
            f"  {AMBER}{row_tot:>7}{R}"
            f"  {DIM}{row_lat:>8}{R}"
            f"  {rc}{star}{R}{notes_str}"
        )

        if resp_preview and cur:
            cache_note = ""
            if cur.get("_cache_read"):
                cache_note = f"  {DIM}cache_read={cur['_cache_read']} cache_create={cur.get('_cache_create',0)}{R}"
            print(f"    {DIM}└─ {resp_preview}{R}{cache_note}")

    # ── Totals ────────────────────────────────────────────────────────────────
    print(f"  {CORAL}{'─'*42} {'─'*8} {'─'*8} {'─'*8}  {'─'*8}  {'─'*14}{R}")
    print(
        f"  {BOLD}{'TOTAL (all models)':<42}{R}"
        f"  {BOLD}{CYAN}{fmt_num(grand_input):>7}{R}"
        f"  {BOLD}{GREEN}{fmt_num(grand_output):>7}{R}"
        f"  {BOLD}{AMBER}{fmt_num(grand_total):>7}{R}"
        f"  {DIM}{'':>8}{R}"
        f"  {DIM}(cumulative){R}"
    )
    print()

    # ── Per-model bar chart ───────────────────────────────────────────────────
    if grand_total > 0:
        print(f"  {BOLD}{CREAM}TOKEN DISTRIBUTION{R}")
        print(f"  {CORAL}{'─' * 60}{R}")
        for m in models:
            if m.get("skip"):
                continue
            mid   = m["id"]
            color = m.get("color", CREAM)
            saved = usage["models"].get(mid, {})
            tot   = saved.get("token_total", 0)
            b     = bar(tot, grand_total, 20)
            pct   = round(tot / grand_total * 100, 1) if grand_total else 0
            lbl   = m["label"][:35]
            print(f"  {color}{lbl:<35}{R} {AMBER}{b}{R} {pct:5.1f}%  {fmt_num(tot):>8} tok")
        print()

    # ── Legend ────────────────────────────────────────────────────────────────
    print(f"  {DIM}INPUT = prompt tokens   OUTPUT = completion tokens   TOTAL = INPUT+OUTPUT{R}")
    print(f"  {DIM}★★★★★ = exceptional  ★★★★☆ = great  ★★★☆☆ = good  ─ = not measured via API{R}")
    print()


# ── Run tests ─────────────────────────────────────────────────────────────────
def run_tests(models: list) -> dict:
    results = {}
    print(f"\n  {BOLD}{CREAM}Running tests against all models...{R}")
    print(f"  {DIM}Prompt: \"{TEST_PROMPT}\"{R}\n")

    for m in models:
        key = m.get("api_key", "")
        is_cli = m.get("provider") == "claude_cli"
        if not key and not is_cli:
            print(f"  {RED}✗{R}  {m['label']:<42} {RED}API key not configured{R}")
            results[m["id"]] = {"error": "API key not configured", "latency": 0}
            continue

        color = m.get("color", CREAM)
        print(f"  {DIM}⏳{R}  {color}{m['label']:<42}{R} ", end="", flush=True)
        res = run_model(m)

        if "error" in res:
            err_short = res["error"][:60]
            print(f"{RED}✗ {err_short}{R}")
        else:
            fb = f" {DIM}[fallback: {m.get('_used_fallback','?')}]{R}" if m.get("_used_fallback") else ""
            print(
                f"{GREEN}✅{R}  "
                f"in={CYAN}{res['input']}{R} "
                f"out={GREEN}{res['output']}{R} "
                f"tot={AMBER}{res['total']}{R} "
                f"lat={DIM}{res['latency']:.2f}s{R}"
                f"{fb}"
            )

        results[m["id"]] = res
    return results


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args      = set(sys.argv[1:])
    stats_only = "--stats" in args
    reset      = "--reset" in args

    cfg    = load_config()
    models = get_models(cfg)
    usage  = load_usage()

    if reset:
        usage = {"models": {}, "last_run": None, "total_runs": 0}
        save_usage(usage)
        print(f"\n  {GREEN}✅ Token usage stats reset.{R}\n")

    results = None
    if not stats_only and not reset:
        results = run_tests(models)
        # Accumulate
        for mid, res in results.items():
            accumulate(usage, mid, res)
        usage["last_run"]    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usage["total_runs"]  = usage.get("total_runs", 0) + 1
        save_usage(usage)

    show_dashboard(models, results, usage)


if __name__ == "__main__":
    main()
