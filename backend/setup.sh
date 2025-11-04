#!/usr/bin/env bash
set -e

echo "Starting setup..."

# Install pyenv if not already installed
if [ ! -d "$HOME/.pyenv" ]; then
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    git clone https://github.com/pyenv/pyenv-doctor.git ~/.pyenv/plugins/pyenv-doctor
    git clone https://github.com/pyenv/pyenv-update.git ~/.pyenv/plugins/pyenv-update
    git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
fi

# Load pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"

# Install a safe Python version for Render Free Plan
PYTHON_VERSION=3.11.8
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
fi

pyenv global $PYTHON_VERSION
python --version
pip --version

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies (safe versions)
pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-multipart==0.0.6 \
    PyPDF2==3.0.1 \
    pypdf==3.17.1 \
    python-docx==1.1.0 \
    requests==2.31.0 \
    pydantic==2.5.3 \
    python-dotenv==1.0.0

echo "Setup complete! ✅ Python and dependencies installed."
