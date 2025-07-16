#!/usr/bin/env python3
"""
Script de teste para validar o carregamento das configurações
"""

from config import DEFAULT_MONTH, DEFAULT_YEAR, debug_config


def main():
    print("🔧 Testando configurações do .env")
    debug_config()

    print(f"\n📅 Período configurado: {DEFAULT_MONTH:02d}/{DEFAULT_YEAR}")
    print(
        f"🗓️  Nome da aba que será criada: Conferência {DEFAULT_MONTH:02d}/{DEFAULT_YEAR} - Script")


if __name__ == "__main__":
    main()
