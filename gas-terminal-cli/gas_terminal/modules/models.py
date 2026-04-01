"""GAS Terminal v3 — Module 6: AI Models & Token Usage"""
from __future__ import annotations
import httpx
from gas_terminal.utils import display as D
from gas_terminal import config

MENU = [
    ("1", "📋", "Lihat Semua AI Models"),
    ("2", "💬", "Chat — Claude (Anthropic)"),
    ("3", "💬", "Chat — DeepSeek / Llama (OpenRouter)"),
    ("4", "💬", "Chat — Kimi AI (Moonshot)"),
    ("5", "💬", "Chat — Gemini (AI Studio)"),
    ("6", "🔀", "Ganti Default Provider"),
    ("7", "🧪", "Test Semua Provider Sekaligus"),
    ("8", "⚙ ", "Model Config (lihat .env)"),
]

# ── Unified AI caller ─────────────────────────────────────────────────

def ask_ai(prompt: str, provider: str = None, model: str = None, max_tokens: int = 1024) -> str:
    """
    Unified AI caller. Provider options: claude, openrouter, kimi, gemini
    Falls back to next available provider automatically.
    """
    prov = provider or config.DEFAULT_AI_PROVIDER

    # Build fallback chain
    chain = _build_fallback_chain(prov)

    for p in chain:
        try:
            result = _call_provider(p, prompt, model, max_tokens)
            if result:
                return result
        except Exception as e:
            D.warning(f"[{p}] failed: {e}, trying next...")

    return "[GAS AI] Semua provider gagal. Cek API key di .env."


def _build_fallback_chain(preferred: str) -> list[str]:
    """Build ordered list of providers to try, starting with preferred."""
    all_providers = ["openrouter", "kimi", "gemini", "claude"]
    chain = [preferred] + [p for p in all_providers if p != preferred]
    # Only include providers that have keys configured
    available = []
    for p in chain:
        if p == "claude"      and config.ANTHROPIC_API_KEY: available.append(p)
        if p == "openrouter"  and config.OPENROUTER_API_KEY: available.append(p)
        if p == "kimi"        and config.KIMI_API_KEY: available.append(p)
        if p == "gemini"      and config.GEMINI_API_KEY: available.append(p)
    return available if available else [preferred]


def _call_provider(provider: str, prompt: str, model: str, max_tokens: int) -> str:
    if provider == "claude":
        return _call_claude(prompt, model or config.MODEL_FAST, max_tokens)
    elif provider == "openrouter":
        return _call_openrouter(prompt, model or config.OPENROUTER_MODEL, max_tokens)
    elif provider == "kimi":
        return _call_kimi(prompt, model or config.KIMI_MODEL, max_tokens)
    elif provider == "gemini":
        return _call_gemini(prompt, model or config.GEMINI_MODEL, max_tokens)
    return None


def _call_claude(prompt: str, model: str, max_tokens: int) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=model, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text


def _call_openrouter(prompt: str, model: str, max_tokens: int) -> str:
    resp = httpx.post(
        f"{config.OPENROUTER_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://gasstrategyai.xyz",
            "X-Title": "GAS Terminal v3",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_kimi(prompt: str, model: str, max_tokens: int) -> str:
    resp = httpx.post(
        f"{config.KIMI_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {config.KIMI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_gemini(prompt: str, model: str, max_tokens: int) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    resp = httpx.post(
        url,
        params={"key": config.GEMINI_API_KEY},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


# ── TUI Module ────────────────────────────────────────────────────────

def run():
    while True:
        choice = D.sub_menu(MENU, "🧠 AI Models & Token Usage")
        if choice == "b":
            break
        elif choice == "1":
            _show_all_models()
        elif choice == "2":
            _chat_loop("claude", config.MODEL_COMPLEX)
        elif choice == "3":
            _pick_and_chat_openrouter()
        elif choice == "4":
            _pick_and_chat_kimi()
        elif choice == "5":
            _chat_loop("gemini", config.GEMINI_MODEL)
        elif choice == "6":
            _change_provider()
        elif choice == "7":
            _test_all_providers()
        elif choice == "8":
            _show_config()
        D.press_enter()


def _show_all_models():
    from rich.table import Table
    from rich import box
    t = Table(title="Available AI Models", box=box.SIMPLE_HEAD, header_style="bold cyan")
    t.add_column("Provider")
    t.add_column("Model ID")
    t.add_column("Status")
    t.add_column("Best For")

    # Claude
    ok = "✅" if config.ANTHROPIC_API_KEY else "❌ no key"
    t.add_row("Claude (Anthropic)", "claude-sonnet-4-6",          ok, "Complex reasoning")
    t.add_row("Claude (Anthropic)", "claude-haiku-4-5-20251001",  ok, "Fast & cheap")

    # OpenRouter
    ok = "✅" if config.OPENROUTER_API_KEY else "❌ no key"
    for name, mid in config.OPENROUTER_MODELS.items():
        t.add_row("OpenRouter", mid, ok, name)

    # Kimi
    ok = "✅" if config.KIMI_API_KEY else "❌ no key"
    for name, mid in config.KIMI_MODELS.items():
        t.add_row("Kimi/Moonshot", mid, ok, name)

    # Gemini
    ok = "✅" if config.GEMINI_API_KEY else "❌ no key"
    for name, mid in config.GEMINI_MODELS.items():
        t.add_row("Gemini (AI Studio)", mid, ok, name)

    # Vertex
    ok = "✅" if config.VERTEX_PROJECT_ID else "❌ no project"
    t.add_row("Vertex AI (GCP)", "gemini-2.0-flash", ok, "Enterprise / RAG")

    D.console.print(t)
    D.info(f"Default provider: [bold cyan]{config.DEFAULT_AI_PROVIDER}[/bold cyan]")


def _chat_loop(provider: str, model: str):
    D.info(f"Chat dengan [{provider}] model={model}. Ketik 'exit' untuk keluar.\n")
    messages_history = []
    while True:
        user_input = D.ask("Kamu")
        if user_input.lower() in ("exit", "quit", "q", ""):
            break
        messages_history.append(user_input)
        with D.spinner(f"Thinking [{provider}]..."):
            pass
        try:
            reply = ask_ai(user_input, provider=provider, model=model)
            D.result_panel(f"{provider.upper()} ({model})", reply, style="cyan")
        except Exception as e:
            D.error(f"Error: {e}")


def _pick_and_chat_openrouter():
    D.info("Available OpenRouter models:")
    items = [(str(i+1), "🤖", f"{name} → {mid}") for i, (name, mid) in enumerate(config.OPENROUTER_MODELS.items())]
    choice = D.sub_menu(items, "Pilih OpenRouter Model")
    models_list = list(config.OPENROUTER_MODELS.values())
    try:
        idx = int(choice) - 1
        model = models_list[idx]
        _chat_loop("openrouter", model)
    except (ValueError, IndexError):
        _chat_loop("openrouter", config.OPENROUTER_MODEL)


def _pick_and_chat_kimi():
    D.info("Kimi/Moonshot models:")
    items = [(str(i+1), "🌙", f"{name}") for i, (name, _) in enumerate(config.KIMI_MODELS.items())]
    choice = D.sub_menu(items, "Pilih Kimi Model")
    models_list = list(config.KIMI_MODELS.values())
    try:
        idx = int(choice) - 1
        model = models_list[idx]
        _chat_loop("kimi", model)
    except (ValueError, IndexError):
        _chat_loop("kimi", config.KIMI_MODEL)


def _change_provider():
    providers = ["claude", "openrouter", "kimi", "gemini"]
    items = [(str(i+1), "🔀", p) for i, p in enumerate(providers)]
    choice = D.sub_menu(items, "Ganti Default AI Provider")
    try:
        idx = int(choice) - 1
        config.DEFAULT_AI_PROVIDER = providers[idx]
        D.success(f"Default provider: {config.DEFAULT_AI_PROVIDER}")
    except (ValueError, IndexError):
        D.warning("Pilihan tidak valid")


def _test_all_providers():
    test_prompt = "Say 'OK' in one word only."
    D.info("Testing all configured providers with a simple prompt...\n")
    for provider in ["claude", "openrouter", "kimi", "gemini"]:
        key_ok = {
            "claude":      bool(config.ANTHROPIC_API_KEY),
            "openrouter":  bool(config.OPENROUTER_API_KEY),
            "kimi":        bool(config.KIMI_API_KEY),
            "gemini":      bool(config.GEMINI_API_KEY),
        }[provider]
        if not key_ok:
            D.warning(f"[{provider}] SKIP — no API key")
            continue
        try:
            result = _call_provider(provider, test_prompt, None, 50)
            D.success(f"[{provider}] ✅  → {result[:60] if result else 'empty'}")
        except Exception as e:
            D.error(f"[{provider}] ❌  → {str(e)[:80]}")


def _show_config():
    D.result_panel("AI Config (.env)", (
        f"DEFAULT_AI_PROVIDER : {config.DEFAULT_AI_PROVIDER}\n\n"
        f"[bold]Claude[/bold]\n"
        f"  ANTHROPIC_API_KEY  : {'SET ✅' if config.ANTHROPIC_API_KEY else 'NOT SET ❌'}\n"
        f"  MODEL_COMPLEX      : {config.MODEL_COMPLEX}\n"
        f"  MODEL_FAST         : {config.MODEL_FAST}\n\n"
        f"[bold]OpenRouter[/bold]\n"
        f"  OPENROUTER_API_KEY : {'SET ✅' if config.OPENROUTER_API_KEY else 'NOT SET ❌'}\n"
        f"  OPENROUTER_MODEL   : {config.OPENROUTER_MODEL}\n\n"
        f"[bold]Kimi / Moonshot[/bold]\n"
        f"  KIMI_API_KEY       : {'SET ✅' if config.KIMI_API_KEY else 'NOT SET ❌'}\n"
        f"  KIMI_MODEL         : {config.KIMI_MODEL}\n\n"
        f"[bold]Gemini AI Studio[/bold]\n"
        f"  GEMINI_API_KEY     : {'SET ✅' if config.GEMINI_API_KEY else 'NOT SET ❌'}\n"
        f"  GEMINI_MODEL       : {config.GEMINI_MODEL}\n\n"
        f"[bold]Vertex AI (GCP)[/bold]\n"
        f"  VERTEX_PROJECT_ID  : {config.VERTEX_PROJECT_ID}\n"
        f"  VERTEX_LOCATION    : {config.VERTEX_LOCATION}\n"
        f"  CREDENTIALS FILE   : {config.VERTEX_CREDENTIALS or 'NOT SET'}"
    ))
