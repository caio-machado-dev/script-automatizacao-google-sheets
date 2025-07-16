import pandas as pd
from datetime import datetime
from google_sheets_utils import get_worksheet
from gspread_dataframe import set_with_dataframe
from gspread_formatting import set_data_validation_for_cell_range, DataValidationRule, BooleanCondition
from config import WORKSHEET1, WORKSHEET2, WORKSHEET3, DEFAULT_MONTH, DEFAULT_YEAR


def filtrar_por_mes(df, coluna_data, mes, ano):
    return df[(df[coluna_data].dt.month == mes) & (df[coluna_data].dt.year == ano)]


# --- Carregar planilhas ---
worksheet_parceiros = get_worksheet(WORKSHEET1)
worksheet_mencoes = get_worksheet(WORKSHEET2)
worksheet_log = get_worksheet(WORKSHEET3)

# --- Parceiros ---
values_parceiros = worksheet_parceiros.get_all_values()
df_parceiros = pd.DataFrame(values_parceiros[4:], columns=values_parceiros[3])
df_parceiros = df_parceiros.dropna(subset=[df_parceiros.columns[0]])

coluna_cpf = next(
    (c for c in df_parceiros.columns if 'cpf' in c.lower()), None)
coluna_arroba = next(
    (c for c in df_parceiros.columns if 'arroba' in c.lower()), None)
coluna_nome = next(
    (c for c in df_parceiros.columns if 'nome' in c.lower()), None)
coluna_telefone = next(
    (c for c in df_parceiros.columns if 'telefone' in c.lower()), None)
coluna_tamanho = next(
    (c for c in df_parceiros.columns if 'tamanho' in c.lower()), None)

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
    'Arroba': [a.strip().lower() for a in arrobas_mencao]
})

# --- LOG de Indicações ---
datas_log = worksheet_log.col_values(1)[2:]
cpfs_log = worksheet_log.col_values(6)[2:]

num_linhas_log = min(len(datas_log), len(cpfs_log))

df_log = pd.DataFrame({
    'Data': pd.to_datetime(datas_log[:num_linhas_log], errors='coerce'),
    'CPF': [c.replace('.', '').replace('-', '').strip().zfill(11) for c in cpfs_log[:num_linhas_log]]
})

# --- Filtro por Mês/Ano ---
mes = DEFAULT_MONTH  # Configurado no arquivo .env
ano = DEFAULT_YEAR   # Configurado no arquivo .env

# Menções
df_filtrado_mencoes = filtrar_por_mes(df_mencoes, 'Data', mes, ano)
df_mencoes_contagem = df_filtrado_mencoes['Arroba'].value_counts(
).reset_index()
df_mencoes_contagem.columns = ['Arroba', 'Qtd. de Menções']

# Indicações
df_filtrado_log = filtrar_por_mes(df_log, 'Data', mes, ano)
df_filtrado_log = df_filtrado_log[df_filtrado_log['CPF'].isin(cpfs_parceiros)]
df_indicacoes_contagem = df_filtrado_log['CPF'].value_counts().reset_index()
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
df_resultado['BLING'] = ''

colunas_finais = ['Nome Completo', 'Instagram', 'CPF', 'Telefone',
                'Tamanho', 'Menções no Mês', 'Indicações no Mês', 'Status', 'BLING']

aba_destino = f"Conferência {mes:02d}/{ano} - Teste"
try:
    worksheet_final = worksheet_parceiros.spreadsheet.worksheet(aba_destino)
    worksheet_final.clear()
except:
    worksheet_final = worksheet_parceiros.spreadsheet.add_worksheet(title=aba_destino, rows=1000, cols=20)

set_with_dataframe(worksheet_final, df_resultado[colunas_finais])

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
