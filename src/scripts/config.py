"""
Configurações do projeto usando variáveis de ambiente
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent.parent / '.env'
# override=True força recarregar
load_dotenv(dotenv_path=env_path, override=True)

# Configurações de Credenciais
CREDENTIALS_JSON = os.getenv(
    'CREDENTIALS_JSON', 'src/scripts/credentials.json')

# Configurações das Planilhas Google Sheets
WORKSHEET1 = os.getenv('WORKSHEET1', '[100 PARCEIROS] PLANILHA GERAL')
WORKSHEET2 = os.getenv('WORKSHEET2', 'Menções da Bázico - Agência Bázico')
WORKSHEET3 = os.getenv('WORKSHEET3', 'LOG | SISTEMA DE INDICAÇÃO')

# Configurações de Data (para filtros)
DEFAULT_MONTH = int(os.getenv('DEFAULT_MONTH', 5))
DEFAULT_YEAR = int(os.getenv('DEFAULT_YEAR', 2025))

# Configurações de Produção
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Validações


def validate_credentials():
    """Valida se o arquivo de credenciais existe"""
    credentials_path = get_credentials_path()
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Arquivo de credenciais não encontrado: {credentials_path}")
    return True


def get_credentials_path() -> str:
    """Retorna o caminho absoluto para o arquivo de credenciais"""
    if os.path.isabs(CREDENTIALS_JSON):
        return CREDENTIALS_JSON
    else:
        # Se for caminho relativo, resolve a partir da raiz do projeto
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / CREDENTIALS_JSON)


def debug_config():
    """Função para debug das configurações"""
    print("=== CONFIGURAÇÕES CARREGADAS ===")
    print(f"DEFAULT_MONTH: {DEFAULT_MONTH}")
    print(f"DEFAULT_YEAR: {DEFAULT_YEAR}")
    print(f"WORKSHEET1: {WORKSHEET1}")
    print(f"WORKSHEET2: {WORKSHEET2}")
    print(f"WORKSHEET3: {WORKSHEET3}")
    print(f"ENVIRONMENT: {ENVIRONMENT}")
    print("=================================")


# Descomente a linha abaixo para debug
# debug_config()
