import pandas as pd  # garantir que pandas está importado
import pandas as pd
from datetime import datetime
from google_sheets_utils import get_worksheet
from gspread_dataframe import set_with_dataframe
from gspread_formatting import set_data_validation_for_cell_range, DataValidationRule, BooleanCondition
from config import WORKSHEET1, WORKSHEET2, WORKSHEET3, DEFAULT_MONTH, DEFAULT_YEAR
from googleapiclient.discovery import build
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(__file__), "credentials.json")


def filtrar_por_mes(df, coluna_data, mes, ano):
    return df[(df[coluna_data].dt.month == mes) & (df[coluna_data].dt.year == ano)]


# --- Carregar planilhas ---
worksheet_parceiros = get_worksheet(WORKSHEET1)
worksheet_mencoes = get_worksheet(WORKSHEET2)
worksheet_log = get_worksheet(WORKSHEET3)

# --- Parceiros ---
values_parceiros = worksheet_parceiros.get_all_values()
header = [str(col) for col in values_parceiros[3]]
# pyright: ignore[reportArgumentType]
df_parceiros = pd.DataFrame(
    values_parceiros[4:], columns=header)  # type: ignore
df_parceiros = df_parceiros.dropna(subset=[str(df_parceiros.columns[0])])

coluna_cpf = next(
    (c for c in df_parceiros.columns if 'cpf' in str(c).lower()), None)
coluna_arroba = next(
    (c for c in df_parceiros.columns if 'arroba' in str(c).lower()), None)
coluna_nome = next(
    (c for c in df_parceiros.columns if 'nome' in str(c).lower()), None)
coluna_telefone = next(
    (c for c in df_parceiros.columns if 'telefone' in str(c).lower()), None)
coluna_tamanho = next(
    (c for c in df_parceiros.columns if 'tamanho' in str(c).lower()), None)

# --- Tratamento de dados ---
df_parceiros['CPF'] = df_parceiros[coluna_cpf].str.replace(
    r'\D', '', regex=True).str.zfill(11)
df_parceiros['CPF_Formatado'] = df_parceiros['CPF'].str.replace(
    r'(\d{3})(\d{3})(\d{3})(\d{2})', r'\1.\2.\3-\4', regex=True)
df_parceiros['Arroba'] = df_parceiros[coluna_arroba].str.strip().str.lower()
df_parceiros['Nome'] = df_parceiros[coluna_nome]
df_parceiros['Telefone'] = df_parceiros[coluna_telefone].fillna('').str.strip()
df_parceiros['Tamanho'] = df_parceiros[coluna_tamanho].fillna('').str.strip()

cpfs_parceiros = df_parceiros['CPF'].unique()

# --- Menções ---
datas_mencoes = worksheet_mencoes.col_values(1)[1:]
arrobas_mencao = worksheet_mencoes.col_values(2)[1:]

df_mencoes = pd.DataFrame({
    'Data': pd.to_datetime(datas_mencoes, dayfirst=True, errors='coerce'),
    'Arroba': [str(a).strip().lower() for a in arrobas_mencao]
})

# --- LOG de Indicações ---
datas_log = worksheet_log.col_values(1)[2:]
cpfs_log = worksheet_log.col_values(6)[2:]

num_linhas_log = min(len(datas_log), len(cpfs_log))

df_log = pd.DataFrame({
    'Data': pd.to_datetime(datas_log[:num_linhas_log], errors='coerce'),
    'CPF': [str(c).replace('.', '').replace('-', '').strip().zfill(11) for c in cpfs_log[:num_linhas_log]]
})

# --- Filtro por Mês/Ano ---
mes = DEFAULT_MONTH  # Configurado no arquivo .env
ano = DEFAULT_YEAR   # Configurado no arquivo .env

# Menções
df_filtrado_mencoes = filtrar_por_mes(df_mencoes, 'Data', mes, ano)
df_mencoes_contagem = pd.Series([str(a) for a in df_filtrado_mencoes['Arroba']],
                                # type: ignore
                                dtype='str').value_counts().reset_index()
df_mencoes_contagem.columns = ['Arroba', 'Qtd. de Menções']

# Indicações
df_filtrado_log = filtrar_por_mes(df_log, 'Data', mes, ano)
df_filtrado_log = df_filtrado_log[df_filtrado_log['CPF'].isin(cpfs_parceiros)]  # type: ignore
df_indicacoes_contagem = pd.Series(
    # type: ignore
    df_filtrado_log['CPF'], dtype='str').value_counts().reset_index()
df_indicacoes_contagem.columns = ['CPF', 'Qtd. de Indicações']

# --- Resultado Final ---
df_resultado = pd.merge(
    df_parceiros[['Nome', 'Arroba', 'CPF',
                'CPF_Formatado', 'Telefone', 'Tamanho']],
    df_mencoes_contagem,
    on='Arroba', how='left'
).merge(
    df_indicacoes_contagem,
    on='CPF', how='left'
)

df_resultado['Qtd. de Menções'] = df_resultado['Qtd. de Menções'].fillna(
    0).astype(int)
df_resultado['Qtd. de Indicações'] = df_resultado['Qtd. de Indicações'].fillna(
    0).astype(int)
df_resultado['Status dos Clientes'] = df_resultado.apply(
    lambda row: '✅' if row['Qtd. de Menções'] >= 4 and row['Qtd. de Indicações'] >= 1 else '❌', axis=1)
df_resultado.drop(columns=['CPF'], inplace=True)
df_resultado.rename(columns={
    'Nome': 'Nome Completo',
    'Arroba': 'Instagram',
    'CPF_Formatado': 'CPF',
    'Telefone': 'Telefone',
    'Tamanho': 'Tamanho',
    'Qtd. de Menções': 'Menções no Mês',
    'Qtd. de Indicações': 'Indicações no Mês',
    'Status dos Clientes': 'Status'
}, inplace=True)

# --- Adiciona Coluna BLING ---
colunas_finais = ['Nome Completo', 'Instagram', 'CPF', 'Telefone',
                    'Tamanho', 'Menções no Mês', 'Indicações no Mês', 'Status', 'BLING']
aba_destino = f"Conferência {mes:02d}/{ano} - Script"

# Antes de sobrescrever, tenta preservar valores manuais da coluna BLING
try:
    worksheet_final_temp = worksheet_parceiros.spreadsheet.worksheet(
        aba_destino)
    values_atual = worksheet_final_temp.get_all_values()
    if values_atual and len(values_atual) > 1:
        header_atual = [str(col) for col in values_atual[0]]
        # pyright: ignore[reportArgumentType]
        df_atual = pd.DataFrame(
            values_atual[1:], columns=header_atual)  # type: ignore
        if 'CPF' in df_atual.columns and 'BLING' in df_atual.columns:
            bling_dict = dict(zip(df_atual['CPF'], df_atual['BLING']))
            df_resultado['BLING'] = df_resultado['CPF'].map(
                lambda cpf: bling_dict.get(cpf, ''))
        else:
            df_resultado['BLING'] = ''
    else:
        df_resultado['BLING'] = ''
except Exception as e:
    df_resultado['BLING'] = ''

try:
    worksheet_final = worksheet_parceiros.spreadsheet.worksheet(aba_destino)
    worksheet_final.clear()
except:
    worksheet_final = worksheet_parceiros.spreadsheet.add_worksheet(
        title=aba_destino, rows=1000, cols=20)

# Garante que a coluna é numérica antes de somar menções privadas
if 'Menções no Mês' in df_resultado.columns:
    df_resultado['Menções no Mês'] = pd.to_numeric(
        # type: ignore
        df_resultado['Menções no Mês'], errors='coerce').fillna(0).astype(int)

# --- Menções Privadas no Google Drive ---
try:
    service = build('drive', 'v3')
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and name contains '[PV]' and trashed = false",
        fields="files(id, name)"
    ).execute()
    pastas_pv = results.get('files', [])
    print(f"Pastas [PV] encontradas: {[p['name'] for p in pastas_pv]}")
    mes_ano_str = f"{mes:02d}-{str(ano)[-2:]}"  # Exemplo: 07-25
    for pasta in pastas_pv:
        nome_pasta = pasta['name']
        id_pasta = pasta['id']
        nome_pessoa = nome_pasta.replace('[PV]', '').strip()
        print(f"Procurando subpasta {mes_ano_str} em {nome_pasta}...")
        results_mes = service.files().list(
            q=f"'{id_pasta}' in parents and mimeType='application/vnd.google-apps.folder' and name = '{mes_ano_str}' and trashed = false",
            fields="files(id, name)"
        ).execute()
        subpastas_mes = results_mes.get('files', [])
        if subpastas_mes:
            id_subpasta = subpastas_mes[0]['id']
            print(f"Subpasta encontrada: {subpastas_mes[0]['name']}")
            results_arquivos = service.files().list(
                q=f"'{id_subpasta}' in parents and trashed = false",
                fields="files(id)"
            ).execute()
            qtd_mencoes_privadas = len(results_arquivos.get('files', []))
            print(f"Arquivos encontrados: {qtd_mencoes_privadas}")
            idx = df_resultado[df_resultado['Nome Completo'].str.strip(
            ) == nome_pessoa].index
            if not idx.empty and qtd_mencoes_privadas > 0:
                print(
                    f"Somando {qtd_mencoes_privadas} menções para {nome_pessoa}")
                df_resultado.loc[idx, 'Menções no Mês'] += qtd_mencoes_privadas
            else:
                print(
                    f"Nenhum parceiro encontrado para {nome_pessoa} ou nenhuma menção privada.")
        else:
            print(f"Subpasta {mes_ano_str} não encontrada em {nome_pasta}.")
except Exception as e:
    print(f"Erro ao buscar menções privadas no Drive: {e}")

# Recalcula o Status após a soma das menções privadas
df_resultado['Status'] = df_resultado.apply(
    lambda row: '✅' if row['Menções no Mês'] >= 4 and row['Indicações no Mês'] >= 1 else '❌', axis=1
)

# --- Linhas de Resumo ---
qtd_indicacoes = df_resultado['Indicações no Mês'].sum()
qtd_indicadores = (df_resultado['Indicações no Mês'] > 0).sum()
qtd_ativos = (df_resultado['Status'] == '✅').sum()

linha_vazia = pd.DataFrame(
    [["" for _ in df_resultado.columns]], columns=df_resultado.columns)
linha_indicacoes = pd.DataFrame(
    [["Quantidade de Indicações", '', '', '', '', '', qtd_indicacoes, '', '']], columns=df_resultado.columns)
linha_indicadores = pd.DataFrame(
    [["Quantidade de Indicadores", '', '', '', '', '', qtd_indicadores, '', '']], columns=df_resultado.columns)
linha_ativos = pd.DataFrame([["Perfis Ativos do Mês", '', '',
                            '', '', '', '', qtd_ativos, '']], columns=df_resultado.columns)

df_resultado_final = pd.concat(
    [df_resultado, linha_vazia, linha_indicacoes, linha_indicadores, linha_ativos], ignore_index=True)

set_with_dataframe(worksheet_final, df_resultado_final[colunas_finais])

# --- Adiciona Checkbox na Coluna BLING ---
bling_col_idx = colunas_finais.index('BLING') + 1
num_linhas = len(df_resultado) + 1  # +1 pelo cabeçalho

rule = DataValidationRule(
    condition=BooleanCondition('BOOLEAN', []),
    showCustomUi=True
)

set_data_validation_for_cell_range(
    worksheet_final,
    f"{chr(64 + bling_col_idx)}2:{chr(64 + bling_col_idx)}{num_linhas}",
    rule
)

print(f"✅ Planilha '{aba_destino}' atualizada com sucesso!")