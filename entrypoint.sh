
#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "🔴 Retrieve CHAT model..."
ollama pull deepseek-r1:1.5b
echo "🟢 Done!"

echo "🔴 Retrieve Embedding model..."
ollama pull mxbai-embed-large
echo "🟢 Done!"


echo "🔴 Retrieve Rerank model..."
ollama pull qwen2.5:3b
echo "🟢 Done!"

# Wait for Ollama process to finish.
wait $pid

# source -> https://stackoverflow.com/questions/78500319/how-to-pull-model-automatically-with-container-creation