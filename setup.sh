#!/bin/bash
# Ideenfinder Setup Script

echo "🚀 Setting up Ideenfinder..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Initialize config
if [ ! -f "config.yaml" ]; then
    if [ -f "config.yaml.example" ]; then
        cp config.yaml.example config.yaml
        echo "✓ Created config.yaml"
    fi
fi

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env"
    fi
fi

# Create outputs directory
mkdir -p outputs
echo "✓ Created outputs directory"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config.yaml - Add your Anthropic API key"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: python ideenfinder.py start"
echo ""
echo "See QUICKSTART.md for detailed instructions."
