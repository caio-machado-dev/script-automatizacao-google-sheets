import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import get_credentials_path


def get_worksheet(worksheet_title: str, worksheet_index: int = 0, credentials_path: str = None):
    """
    Conecta e retorna uma worksheet do Google Sheets

    Args:
        worksheet_title: Nome da planilha no Google Sheets
        worksheet_index: Índice da aba (padrão: 0)
        credentials_path: Caminho para o arquivo de credenciais (opcional)

    Returns:
        gspread.Worksheet: Objeto da worksheet
    """
    if credentials_path is None:
        credentials_path = get_credentials_path()

    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        filename=credentials_path, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open(title=worksheet_title).get_worksheet(worksheet_index)
