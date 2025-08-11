#!/bin/bash
# filepath: /Users/auvarifqi.diandra/Documents/audio_app/setup.sh

echo "🚀 Setting up Audio Recording App environment..."

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "✅ Conda detected. Setting up conda environment..."
    
    # Ask for environment name
    read -p "Enter name for conda environment (default: audio_app): " ENV_NAME
    ENV_NAME=${ENV_NAME:-audio_app}
    
    # Create conda environment
    echo "🔧 Creating conda environment '$ENV_NAME'..."
    conda create -y -n $ENV_NAME python=3.9
    
    # Activate environment
    echo "🔌 Activating environment..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate $ENV_NAME
    
    # Install requirements
    echo "📦 Installing packages from requirements.txt..."
    pip install -r requirements.txt
    
    echo "🎉 Setup complete! Activate your environment with:"
    echo "conda activate $ENV_NAME"
    
else
    echo "🐍 Conda not found, setting up Python virtual environment instead..."
    
    # Check if python3 is available
    if command -v python3 &> /dev/null; then
        # Create virtual environment
        echo "🔧 Creating virtual environment..."
        python3 -m venv venv
        
        # Activate virtual environment
        echo "🔌 Activating environment..."
        if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
            source venv/bin/activate
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            source venv/Scripts/activate
        fi
        
        # Install requirements
        echo "📦 Installing packages from requirements.txt..."
        pip install -r requirements.txt
        
        echo "🎉 Setup complete! Activate your environment with:"
        if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "source venv/bin/activate"
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            echo "source venv/Scripts/activate"
        fi
        
    else
        echo "❌ Error: Neither conda nor python3 found. Please install one of them and try again."
        exit 1
    fi
fi

# Add instructions for running the app
echo ""
echo "📝 To run the app after activating the environment:"
echo "streamlit run app.py"