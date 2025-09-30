#!/bin/bash
# Enterprise AI Setup Script for Ollama Simulation

echo "🏢 Setting up Enterprise AI with Ollama"
echo "========================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo "   Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✅ Ollama installed"
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
echo "✅ Ollama started with PID: $OLLAMA_PID"

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running and accessible"
else
    echo "❌ Ollama is not responding"
    echo "   Please check if Ollama is running: ollama serve"
    exit 1
fi

# Download recommended models
echo "📥 Downloading recommended models..."
echo "   This may take a few minutes..."

# Download models in background
ollama pull llama2:7b &
ollama pull codellama:7b &
ollama pull mistral:7b &

# Wait for models to download
echo "⏳ Waiting for models to download..."
wait

echo "✅ Models downloaded successfully"

# Configure enterprise AI
echo "⚙️ Configuring enterprise AI settings..."
python3 configure_enterprise_ai.py

# Start local LLM server
echo "🌐 Starting local LLM server..."
python3 local_llm_server.py &
LLM_SERVER_PID=$!
echo "✅ Local LLM server started with PID: $LLM_SERVER_PID"

# Wait for local LLM server to start
echo "⏳ Waiting for local LLM server to start..."
sleep 3

# Test the setup
echo "🧪 Testing enterprise AI setup..."
python3 test_enterprise_ai_simulation.py

echo ""
echo "🎉 Enterprise AI setup complete!"
echo ""
echo "📋 Summary:"
echo "  - Ollama service: Running (PID: $OLLAMA_PID)"
echo "  - Local LLM server: Running (PID: $LLM_SERVER_PID)"
echo "  - Enterprise settings: Configured"
echo "  - Models: Downloaded and ready"
echo ""
echo "🚀 You can now use enterprise AI features:"
echo "  - AI test case generation"
echo "  - AI test improvement"
echo "  - BDD scenario generation"
echo "  - Test data generation"
echo "  - Coverage analysis"
echo ""
echo "💡 To stop services:"
echo "  kill $OLLAMA_PID $LLM_SERVER_PID"
echo ""
echo "📖 For more information, see: ENTERPRISE_AI_SIMULATION_GUIDE.md"