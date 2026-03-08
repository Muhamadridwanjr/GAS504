#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║     GAS — Claude CLI Setup Script                          ║
# ║     Ubuntu 20.04 | Node.js upgrade + Claude install        ║
# ╚══════════════════════════════════════════════════════════════╝
#
# CARA PAKAI:
#   chmod +x setup-claude.sh
#   ./setup-claude.sh
#
# STEP YANG DILAKUKAN:
#   1. Hapus Node.js lama
#   2. Install Node.js 20 LTS
#   3. Install Claude Code CLI
#   4. Login Claude (Pro $20)
#   5. Verifikasi semua

set -e  # Stop kalau ada error

# ── WARNA ─────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; WHITE='\033[1;37m'; DIM='\033[2m'; NC='\033[0m'

ok()   { echo -e "${GREEN}  ✅ $1${NC}"; }
err()  { echo -e "${RED}  ❌ $1${NC}"; exit 1; }
info() { echo -e "${CYAN}  ➤  $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠️  $1${NC}"; }
head() { echo -e "\n${WHITE}$1${NC}"; echo -e "${DIM}$(printf '─%.0s' {1..54})${NC}"; }

echo -e "${CYAN}"
cat << 'EOF'
   ██████╗ ██╗      █████╗ ██╗   ██╗██████╗ ███████╗
  ██╔════╝ ██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝
  ██║      ██║     ███████║██║   ██║██║  ██║█████╗
  ██║      ██║     ██╔══██║██║   ██║██║  ██║██╔══╝
  ╚██████╗ ███████╗██║  ██║╚██████╔╝██████╔╝███████╗
   ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
EOF
echo -e "${NC}"
echo -e "${WHITE}  Claude CLI Setup — Ubuntu 20.04${NC}"
echo -e "${DIM}  Node.js upgrade + Claude Code install${NC}\n"

# ── CEK ROOT / SUDO ───────────────────────────────────────────
if [ "$EUID" -eq 0 ]; then
    warn "Running sebagai root. Sebaiknya pakai user biasa + sudo."
fi

# ── STEP 1: HAPUS NODE LAMA ───────────────────────────────────
head "STEP 1 — Hapus Node.js lama"
info "Menghapus Node.js versi lama..."

sudo apt-get remove -y nodejs npm 2>/dev/null || true
sudo apt-get autoremove -y 2>/dev/null || true
sudo rm -f /usr/local/bin/node /usr/local/bin/npm /usr/local/bin/npx 2>/dev/null || true

# Hapus nvm kalau ada
if [ -f "$HOME/.nvm/nvm.sh" ]; then
    warn "NVM terdeteksi. Menonaktifkan NVM node..."
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm deactivate 2>/dev/null || true
fi

ok "Node.js lama sudah dihapus"

# ── STEP 2: INSTALL NODE.JS 20 ───────────────────────────────
head "STEP 2 — Install Node.js 20 LTS"
info "Download NodeSource setup script..."

curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

info "Install Node.js 20..."
sudo apt-get install -y nodejs

# Verifikasi
NODE_VER=$(node --version 2>/dev/null || echo "not found")
NPM_VER=$(npm --version 2>/dev/null || echo "not found")

if [[ "$NODE_VER" == v2* ]]; then
    ok "Node.js $NODE_VER terinstall"
    ok "npm $NPM_VER terinstall"
else
    err "Node.js install gagal! Version: $NODE_VER"
fi

# ── STEP 3: SETUP NPM GLOBAL (tanpa sudo) ─────────────────────
head "STEP 3 — Konfigurasi npm global"
info "Setup npm global directory tanpa sudo..."

mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"

# Tambah ke PATH kalau belum ada
PROFILE_FILE="$HOME/.bashrc"
if ! grep -q ".npm-global" "$PROFILE_FILE" 2>/dev/null; then
    echo '' >> "$PROFILE_FILE"
    echo '# npm global (no sudo)' >> "$PROFILE_FILE"
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> "$PROFILE_FILE"
    ok "PATH ditambahkan ke $PROFILE_FILE"
fi

export PATH="$HOME/.npm-global/bin:$PATH"
ok "npm global path dikonfigurasi: $HOME/.npm-global"

# ── STEP 4: INSTALL CLAUDE CODE CLI ──────────────────────────
head "STEP 4 — Install Claude Code CLI"
info "Installing @anthropic-ai/claude-code..."

npm install -g @anthropic-ai/claude-code

# Verifikasi
CLAUDE_PATH=$(which claude 2>/dev/null || echo "")
if [ -z "$CLAUDE_PATH" ]; then
    # Coba dari npm global path langsung
    CLAUDE_PATH="$HOME/.npm-global/bin/claude"
fi

if [ -f "$CLAUDE_PATH" ]; then
    CLAUDE_VER=$("$CLAUDE_PATH" --version 2>/dev/null || echo "unknown")
    ok "Claude CLI terinstall: $CLAUDE_VER"
    ok "Path: $CLAUDE_PATH"
else
    err "Claude CLI tidak ditemukan setelah install!"
fi

# ── STEP 5: CEK ANTHROPIC_API_KEY ────────────────────────────
head "STEP 5 — Cek environment variables"

if [ -n "$ANTHROPIC_API_KEY" ]; then
    warn "ANTHROPIC_API_KEY terdeteksi di environment!"
    warn "Ini akan pakai billing API, BUKAN quota Pro \$20 lo!"
    echo ""
    echo -e "  ${WHITE}Solusi:${NC} Hapus dari ~/.bashrc atau ~/.profile:"
    echo -e "  ${DIM}  # Cari baris ini dan hapus/comment:${NC}"
    echo -e "  ${CYAN}  export ANTHROPIC_API_KEY=sk-ant-...${NC}"
    echo ""
    read -p "  Mau otomatis comment-out sekarang? (y/n): " REMOVE_KEY
    if [ "$REMOVE_KEY" = "y" ]; then
        sed -i 's/^export ANTHROPIC_API_KEY/# export ANTHROPIC_API_KEY/' "$HOME/.bashrc"
        sed -i 's/^export ANTHROPIC_API_KEY/# export ANTHROPIC_API_KEY/' "$HOME/.profile" 2>/dev/null || true
        unset ANTHROPIC_API_KEY
        ok "ANTHROPIC_API_KEY sudah di-comment. Reload: source ~/.bashrc"
    fi
else
    ok "ANTHROPIC_API_KEY tidak ditemukan — Claude akan pakai quota Pro \$20"
fi

# ── STEP 6: LOGIN CLAUDE ──────────────────────────────────────
head "STEP 6 — Login Claude Pro \$20"

echo -e "  ${WHITE}Pilih metode login:${NC}"
echo -e "  ${CYAN}1.${NC} Login via browser (buka URL di browser lo)"
echo -e "  ${CYAN}2.${NC} Skip login sekarang (manual nanti)"
echo ""
read -p "  Pilih (1/2): " LOGIN_CHOICE

if [ "$LOGIN_CHOICE" = "1" ]; then
    info "Membuka login Claude..."
    echo ""
    echo -e "  ${YELLOW}Langkah:${NC}"
    echo -e "  1. URL akan muncul di bawah"
    echo -e "  2. Buka URL itu di browser lo"
    echo -e "  3. Login dengan akun Claude Pro lo"
    echo -e "  4. Kembali ke sini setelah berhasil"
    echo ""
    "$CLAUDE_PATH" login || warn "Login gagal atau dibatalkan"
else
    warn "Login di-skip. Jalankan manual nanti: claude login"
fi

# ── STEP 7: CEK TMUX ──────────────────────────────────────────
head "STEP 7 — Cek & Install tmux"

if command -v tmux &>/dev/null; then
    TMUX_VER=$(tmux -V)
    ok "tmux sudah ada: $TMUX_VER"
else
    info "Install tmux..."
    sudo apt-get install -y tmux
    ok "tmux terinstall!"
fi

# ── STEP 8: CEK GAS TOOLS ────────────────────────────────────
head "STEP 8 — Cek gas-tools.py"

GAS_SCRIPT="$HOME/goldenaistrategy/gas-tools.py"
if [ -f "$GAS_SCRIPT" ]; then
    ok "gas-tools.py ditemukan: $GAS_SCRIPT"
else
    warn "gas-tools.py belum ada di ~/goldenaistrategy/"
    echo -e "  ${DIM}Upload dulu: scp gas-tools.py user@IP:~/goldenaistrategy/${NC}"
fi

# ── SUMMARY ───────────────────────────────────────────────────
head "✅ SETUP SELESAI"

echo ""
echo -e "  ${WHITE}Verifikasi:${NC}"
echo -e "  Node.js : $(node --version 2>/dev/null || echo 'NOT FOUND')"
echo -e "  npm     : $(npm --version 2>/dev/null || echo 'NOT FOUND')"
echo -e "  claude  : $("$CLAUDE_PATH" --version 2>/dev/null || echo 'NOT FOUND')"
echo -e "  tmux    : $(tmux -V 2>/dev/null || echo 'NOT FOUND')"
echo ""
echo -e "  ${WHITE}Cara mulai:${NC}"
echo -e "  ${CYAN}source ~/.bashrc${NC}         # reload PATH"
echo -e "  ${CYAN}claude login${NC}             # kalau belum login"
echo -e "  ${CYAN}tmux new -s gas${NC}          # buat tmux session"
echo -e "  ${CYAN}python3 gas-tools.py${NC}     # jalankan GAS Tools"
echo ""
echo -e "  ${GREEN}🚀 Gas bro!${NC}"
echo ""
