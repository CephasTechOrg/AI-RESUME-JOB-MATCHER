#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# -------------------------------
# 1️⃣ Specify Python version
# -------------------------------
PYTHON_VERSION=3.14.0

# Install pyenv if not already installed (Render Linux default)
if ! command -v pyenv >/dev/null 2>&1; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash

    # Setup pyenv environment for this shell
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
fi

# Install and set desired Python version
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
fi
pyenv global $PYTHON_VERSION
echo "Using Python version: $(python --version)"

# -------------------------------
# 2️⃣ Upgrade pip
# -------------------------------
pip install --upgrade pip
echo "Upgraded pip to: $(pip --version)"

# -------------------------------
# 3️⃣ Install project dependencies
# -------------------------------
pip install \
fastapi==0.104.1 \
uvicorn==0.24.0 \
python-multipart==0.0.6 \
PyPDF2==3.0.1 \
pypdf==3.17.1 \
python-docx==1.1.0 \
requests==2.31.0 \
pydantic==2.5.3 \
python-dotenv==1.0.0

echo "Dependencies installed successfully!"
