#!/usr/bin/env python3
"""
Colab cache temizleme ve güncel repo'yu zorlama scripti
Kullanım: python clear_colab_cache.py
"""

import os
import shutil
import subprocess
from pathlib import Path

def clear_jupyter_cache():
    """Jupyter ve IPython cache'lerini temizle"""
    print("📦 Jupyter cache temizleniyor...")
    cache_dirs = [
        Path.home() / ".cache" / "jupyter",
        Path("/root/.cache/jupyter"),
        Path.home() / ".ipython",
        Path("/root/.ipython"),
    ]
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                print(f"  ✓ Silindi: {cache_dir}")
            except Exception as e:
                print(f"  ⚠ Silinemedi {cache_dir}: {e}")

def clear_notebook_checkpoints():
    """Notebook checkpoint'lerini temizle"""
    print("🗑️  Notebook checkpoints temizleniyor...")
    count = 0
    for checkpoint_dir in Path.cwd().rglob(".ipynb_checkpoints"):
        try:
            shutil.rmtree(checkpoint_dir)
            count += 1
        except Exception as e:
            print(f"  ⚠ Silinemedi {checkpoint_dir}: {e}")
    print(f"  ✓ {count} checkpoint klasörü silindi")

def clear_python_cache():
    """Python cache dosyalarını temizle"""
    print("🐍 Python cache temizleniyor...")
    pycache_count = 0
    pyc_count = 0
    
    for pycache_dir in Path.cwd().rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            pycache_count += 1
        except Exception as e:
            print(f"  ⚠ Silinemedi {pycache_dir}: {e}")
    
    for pyc_file in Path.cwd().rglob("*.pyc"):
        try:
            pyc_file.unlink()
            pyc_count += 1
        except Exception as e:
            print(f"  ⚠ Silinemedi {pyc_file}: {e}")
    
    print(f"  ✓ {pycache_count} __pycache__ klasörü, {pyc_count} .pyc dosyası silindi")

def force_git_update():
    """Git cache temizle ve güncel sürümü zorla"""
    print("🔄 Git cache temizleniyor ve güncel sürüm çekiliyor...")
    commands = [
        ["git", "clean", "-fd"],
        ["git", "reset", "--hard", "HEAD"],
        ["git", "fetch", "origin"],
        ["git", "reset", "--hard", "origin/main"],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"  ✓ {' '.join(cmd)}")
            if result.stdout.strip():
                print(f"    {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠ Hata: {' '.join(cmd)}")
            if e.stderr:
                print(f"    {e.stderr.strip()}")

def main():
    print("🧹 Colab cache temizleniyor ve güncel repo çekiliyor...\n")
    
    clear_jupyter_cache()
    print()
    
    clear_notebook_checkpoints()
    print()
    
    clear_python_cache()
    print()
    
    force_git_update()
    print()
    
    print("✅ Cache temizlendi ve güncel repo sürümü yüklendi!")
    print("📝 Şimdi notebook'u yeniden açın ve çalıştırın.")
    print("\nColab'da çalıştırmak için:")
    print("  !python clear_colab_cache.py")

if __name__ == "__main__":
    main()
