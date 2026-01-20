#!/bin/bash
# Colab cache temizleme ve güncel repo'yu zorlama scripti

echo "🧹 Colab cache temizleniyor ve güncel repo çekiliyor..."

# Jupyter/Colab cache temizle
echo "📦 Jupyter cache temizleniyor..."
rm -rf ~/.cache/jupyter 2>/dev/null || true
rm -rf /root/.cache/jupyter 2>/dev/null || true
rm -rf ~/.ipython 2>/dev/null || true
rm -rf /root/.ipython 2>/dev/null || true

# Notebook checkpoints temizle
echo "🗑️  Notebook checkpoints temizleniyor..."
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

# Git cache temizle ve hard reset
echo "🔄 Git cache temizleniyor ve güncel sürüm çekiliyor..."
git clean -fd
git reset --hard HEAD
git fetch origin
git reset --hard origin/main

# Python cache temizle
echo "🐍 Python cache temizleniyor..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Cache temizlendi ve güncel repo sürümü yüklendi!"
echo "📝 Şimdi notebook'u yeniden açın ve çalıştırın."
