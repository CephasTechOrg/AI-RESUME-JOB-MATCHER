#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Installing Rust toolchain..."
curl https://sh.rustup.rs -sSf | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"
echo "✅ Rust toolchain installed."

cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed."

