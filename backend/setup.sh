#!/usr/bin/env bash
set -e

echo "Starting setup for Render Free Plan..."

# 1. Install pyenv if missing
if [ ! -d "$HOME/.pyenv" ]; then
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# 2. Install compatible Python
PYTHON_VERSION="3.11.8"
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION\$"; then
    pyenv install $PYTHON_VERSION
fi
pyenv global $PYTHON_VERSION

# 3. Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# 4. Create and activate virtualenv
ENV_NAME="render-env"
if ! pyenv virtualenvs | grep -q $ENV_NAME; then
    pyenv virtualenv $PYTHON_VERSION $ENV_NAME
fi
pyenv activate $ENV_NAME

# 5. Install dependencies
pip install fastapi==0.104.1 uvicorn==0.23.2 python-multipart==0.0.6 \
            PyPDF2==3.0.1 python-docx==0.8.11 requests==2.31.0 \
            pydantic==2.5.3 python-dotenv==1.0.0

echo "Setup complete. Python version: $(python --version)"
echo "Virtualenv active: $(which python)"

# 6. Run the app using the virtualenv path
$PYENV_ROOT/versions/$ENV_NAME/bin/uvicorn main:app --host 0.0.0.0 --port 10000
