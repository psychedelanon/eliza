#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# ─────────────────────────────────────────────────────────────────────
# 🟢 ElizaOS / Sproto stack – Codex bootstrap (no Docker required)
# ─────────────────────────────────────────────────────────────────────

_say() { printf "\033[1;36m▶ %s\033[0m\n" "$*"; }
_ok()  { printf "\033[0;32m✓ %s\033[0m\n" "$*"; }
_warn(){ printf "\033[1;33m⚠ %s\033[0m\n" "$*"; }

# 1. Soft‑check Docker
if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
  _warn "Docker unavailable – continuing (Codex sandbox has no Docker)"
else
  _ok "Docker running"
fi

# 2. Node 23.3.0 via nvm
export NVM_DIR="$HOME/.nvm"
need_node=23.3.0
have_node=0
if command -v node >/dev/null 2>&1; then
  have_node=$(node -v | sed 's/v//')
fi
if [[ "$have_node" != "$need_node" ]]; then
  _say "Installing Node $need_node via nvm"
  [ -s "$NVM_DIR/nvm.sh" ] || curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  # shellcheck source=/dev/null
  source "$NVM_DIR/nvm.sh"
  nvm install "$need_node"
  nvm use "$need_node"
  nvm alias default "$need_node"
fi
_ok "Node $(node -v)"

# 3. Bun
export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
export PATH="$BUN_INSTALL/bin:$PATH"
if ! command -v bun >/dev/null 2>&1; then
  _say "Installing Bun"
  curl -fsSL https://bun.sh/install | bash -s -- --yes
fi
_ok "Bun $(bun --version)"

# 4. Git submodules
if [ -f .gitmodules ]; then
  _say "Initialising submodules"
  git submodule update --init --recursive
fi

# 5. Clean up any existing dependencies
_say "Cleaning up existing dependencies..."
rm -rf node_modules
rm -f package-lock.json
rm -f bun.lockb
rm -f yarn.lock

# 6. Install + build
_say "bun install"
bun install

_say "bun run build"
bun run build

# 7. Optional tests
if [ -x scripts/test.sh ]; then
  _say "Running scripts/test.sh"
  scripts/test.sh
fi

_ok "Environment ready" 