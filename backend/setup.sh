#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting setup for Render Free Plan..."

# -------------------------
# 1. Install pyenv if missing
# -------------------------
if [ ! -d "$HOME/.pyenv" ]; then
    echo "Installing pyenv..."
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
fi

# Add pyenv to PATH
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# -------------------------
# 2. Install compatible Python
# -------------------------
PYTHON_VERSION="3.11.8"

if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION\$"; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
fi

pyenv global $PYTHON_VERSION

# -------------------------
# 3. Upgrade pip and setuptools
# -------------------------
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# -------------------------
# 4. Install dependencies
# -------------------------
echo "Installing dependencies..."

# Use compatible versions to avoid maturin/Rust compilation
pip install fastapi==0.104.1 \
            uvicorn==0.23.2 \
            python-multipart==0.0.6 \
            PyPDF2==3.0.1 \
            python-docx==0.8.11 \
            requests==2.31.0 \
            pydantic==2.5.3 \
            python-dotenv==1.0.0

echo "Setup complete. Python version: $(python --version)"
