#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Installing Rust toolchain..."
curl https://sh.rustup.rs -sSf | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"

echo "📦 Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "🐍 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "✅ Build completed successfully!"
