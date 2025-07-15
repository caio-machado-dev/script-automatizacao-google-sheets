# 📊 Script-Automatização-Planilhas-Bázico

Sistema automatizado para análise de performance de parceiros da Bázico, integrando dados de menções no Instagram e indicações de clientes através de planilhas Google Sheets.

## 🎯 Funcionalidades

- **Análise de Menções**: Conta menções de parceiros no Instagram por período
- **Tracking de Indicações**: Monitora indicações realizadas pelos parceiros
- **Relatório Automatizado**: Gera relatórios mensais com status de performance
- **Integração Google Sheets**: Conecta e atualiza planilhas automaticamente
- **Validação de Status**: Define status dos parceiros baseado em critérios específicos

## 📋 Critérios de Performance

Um parceiro recebe status ✅ se:

- **Menções**: Mais ou igual a 4 menções no mês
- **Indicações**: Mais ou igual a 1 indicação no mês

Caso contrário, recebe status ❌

## 🗂️ Estrutura do Projeto

```
Script-Automatização-Planilhas-Bázico/
├── src/
│   └── scripts/
│       ├── conection_worksheets.py    # Script principal de análise
│       ├── google_sheets_utils.py     # Utilitários para Google Sheets
│       ├── lower_case_column.py       # Utilitário para normalização
│       ├── config.py                  # Configurações do projeto
│       └── documentation_scripts.ipynb # Documentação em Jupyter
├── .env                               # Variáveis de ambiente (não versionado)
├── .env.example                       # Exemplo de configuração
├── CREDENTIALS_SETUP.md              # Guia de configuração
├── pyproject.toml                    # Dependências do projeto
└── README.md                         # Esta documentação
```

## 📊 Planilhas Utilizadas

O sistema integra com 3 planilhas Google Sheets:

1. **[100 PARCEIROS] PLANILHA GERAL**: Dados dos parceiros (nome, CPF, Instagram)
2. **Menções da Bázico - Agência Bázico**: Log de menções no Instagram
3. **LOG | SISTEMA DE INDICAÇÃO**: Registro de indicações por CPF

## 🚀 Instalação e Configuração

### 1. Requisitos

- Python 3.12+
- Conta Google Cloud com APIs habilitadas
- Acesso às planilhas Google Sheets

### 2. Instalar Dependências

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd Script-Automatização-Planilhas-Bázico

# Instalar com uv (recomendado)
uv sync

# Ou com pip
pip install -e .
```

### 3. Configurar Credenciais

1. Siga o guia detalhado em [`CREDENTIALS_SETUP.md`](CREDENTIALS_SETUP.md)
2. Configure o arquivo `.env` baseado no `.env.example`
3. Baixe e configure o arquivo `credentials.json`

### 4. Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as configurações
nano .env
```

## 🛠️ Uso

### Executar Análise Principal

```bash
cd src/scripts
python conection_worksheets.py
```

### Funcionalidades do Script Principal

O script `conection_worksheets.py` executa:

1. **Carrega dados** das 3 planilhas configuradas
2. **Processa CPFs** removendo formatação e validando
3. **Normaliza arrobas** do Instagram (lowercase)
4. **Filtra por período** usando mês/ano configurados
5. **Conta menções** por arroba no período
6. **Conta indicações** por CPF no período
7. **Calcula status** baseado nos critérios
8. **Gera relatório** em nova aba da planilha

### Exemplo de Saída

| Nome Completo | Instagram | CPF            | Menções no Mês | Indicações no Mês | Status |
| ------------- | --------- | -------------- | -------------- | ----------------- | ------ |
| João Silva    | @joao123  | 123.456.789-00 | 6              | 2                 | ✅     |
| Maria Santos  | @maria456 | 987.654.321-00 | 3              | 1                 | ❌     |

## ⚙️ Configurações

### Variáveis de Ambiente (.env)

```properties
# Script-Automatização-Planilhas-Bázico
# Configurações de exemplo

# Credenciais
CREDENTIALS_JSON="src/scripts/credentials.json"

# Planilhas (Exemplos fictícios)
WORKSHEET1="Planilha Parceiros Exemplo"
WORKSHEET2="Planilha Menções Exemplo"
WORKSHEET3="Planilha Log Indicações Exemplo"

# Período de análise
DEFAULT_MONTH=1
DEFAULT_YEAR=2024

# Ambiente
ENVIRONMENT="development"
```

### Personalizar Período

Para analisar um período específico, modifique no `.env`:

```properties
DEFAULT_MONTH=7    # Julho
DEFAULT_YEAR=2025  # 2025
```

## 📦 Dependências

- **pandas**: Manipulação de dados
- **gspread**: Integração Google Sheets
- **gspread-dataframe**: Export de DataFrames
- **oauth2client**: Autenticação Google (será migrado para google-auth)
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🔧 Scripts Auxiliares

### `lower_case_column.py`

Utilitário para normalizar dados de uma coluna específica para lowercase.

### `google_sheets_utils.py`

Módulo com funções para conexão e manipulação das planilhas Google Sheets.

### `config.py`

Gerenciamento centralizado de configurações usando variáveis de ambiente.

## 🚀 Deploy para Produção

### Opções de Deploy

1. **Google Cloud Functions** (Recomendado para este projeto)
2. **AWS Lambda**
3. **Heroku**
4. **VPS tradicional**

### Checklist Pré-Produção

- [ ] Configurar gerenciador de secrets (Google Secret Manager, AWS Secrets Manager)
- [ ] Configurar variáveis de ambiente no servidor
- [ ] Implementar logs estruturados
- [ ] Configurar monitoramento e alertas
- [ ] Testes de integração
- [ ] Migrar de `oauth2client` para `google-auth`

## 🔒 Segurança

- ✅ Credenciais protegidas no `.gitignore`
- ✅ Uso de variáveis de ambiente
- ✅ Documentação de configuração segura
- ⚠️ **NUNCA** commitar `credentials.json` ou `.env`

## 🐛 Troubleshooting

### Erro: "Arquivo de credenciais não encontrado"

1. Verifique se `credentials.json` está em `src/scripts/`
2. Confirme as permissões do arquivo
3. Valide o caminho no `.env`

### Erro: "Permission denied" no Google Sheets

1. Verifique se as planilhas foram compartilhadas com o email da conta de serviço
2. Confirme se a conta tem permissão de "Editor"
3. Verifique se as APIs estão habilitadas no Google Cloud

### Erro de Importação

```bash
# Reinstalar dependências
uv sync --force

# Ou verificar ambiente Python
python --version
pip list
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário da Agência Bázico.

## 📞 Suporte

Para dúvidas ou problemas:

- Consulte a documentação em `CREDENTIALS_SETUP.md`
- Verifique os logs de execução
- Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido com ❤️ para Agência Bázico**
