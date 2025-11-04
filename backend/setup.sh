#!/usr/bin/env bash
# setup.sh
# Self-contained setup for Render Free Plan

# Exit immediately if a command fails
set -e

echo "Starting setup..."

# Install pyenv (for managing Python versions)
if [ ! -d "$HOME/.pyenv" ]; then
    echo "Installing pyenv..."
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    git clone https://github.com/pyenv/pyenv-doctor.git ~/.pyenv/plugins/pyenv-doctor
    git clone https://github.com/pyenv/pyenv-update.git ~/.pyenv/plugins/pyenv-update
    git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
fi

# Load pyenv into the shell
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"

# Install Python 3.12.13 (most compatible with Render Free Plan)
if ! pyenv versions | grep -q "3.12.13"; then
    echo "Installing Python 3.12.13..."
    pyenv install 3.12.13
fi

pyenv global 3.12.13
python --version
pip --version

# Upgrade pip to latest
python -m pip install --upgrade pip

# Install all required Python packages (safe versions)
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

echo "Setup complete! ✅ Python and dependencies are installed."
