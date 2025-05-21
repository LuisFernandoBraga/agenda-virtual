#!/usr/bin/env python
"""
Script para debug do ambiente da Vercel.
"""
import os
import sys
import platform
import site
import json

def main():
    """Exibe informações sobre o ambiente Python para debug."""
    
    info = {
        "Python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "path": sys.path,
            "prefix": sys.prefix,
            "site_packages": site.getsitepackages() if hasattr(site, 'getsitepackages') else "N/A"
        },
        "Environment": {
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "listdir": os.listdir(".")
        },
        "Environment Variables": {var: value for var, value in os.environ.items()}
    }
    
    # Remover informações sensíveis
    for key in list(info["Environment Variables"].keys()):
        if any(sensitive in key.lower() for sensitive in ["key", "secret", "password", "token"]):
            info["Environment Variables"][key] = "[REDACTED]"
    
    print(json.dumps(info, indent=2))

if __name__ == "__main__":
    main() 