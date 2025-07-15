# Guia de Configuração das Credenciais Google Sheets

## 1. Criar um Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. No menu lateral, vá em "APIs e Serviços" > "Biblioteca"
4. Ative as seguintes APIs:
   - Google Sheets API
   - Google Drive API

## 2. Criar uma Conta de Serviço

1. No Google Cloud Console, vá em "APIs e Serviços" > "Credenciais"
2. Clique em "Criar Credenciais" > "Conta de serviço"
3. Preencha:
   - Nome: `bazico-sheets-service`
   - Descrição: `Conta de serviço para acessar planilhas da Bázico`
4. Clique em "Criar e continuar"
5. Pule as etapas opcionais e clique em "Concluir"

## 3. Gerar Chave JSON

1. Na lista de contas de serviço, clique na conta criada
2. Vá para a aba "Chaves"
3. Clique em "Adicionar chave" > "Criar nova chave"
4. Selecione "JSON" e clique em "Criar"
5. O arquivo será baixado automaticamente

## 4. Configurar o Arquivo de Credenciais

1. Renomeie o arquivo baixado para `credentials.json`
2. Mova o arquivo para `src/scripts/credentials.json`
3. **IMPORTANTE**: Nunca commite este arquivo no Git!

## 5. Compartilhar Planilhas com a Conta de Serviço

1. Abra o arquivo `credentials.json`
2. Copie o valor do campo `client_email`
3. No Google Sheets, abra cada planilha que você quer acessar
4. Clique em "Compartilhar"
5. Cole o email da conta de serviço
6. Dê permissão de "Editor"
7. Desmarque "Notificar pessoas" se não quiser enviar email

## 6. Estrutura do arquivo credentials.json

```json
{
  "type": "service_account",
  "project_id": "seu-projeto-id",
  "private_key_id": "id-da-chave",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "nome-da-conta@projeto.iam.gserviceaccount.com",
  "client_id": "id-do-cliente",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "url-do-certificado"
}
```

## 7. Teste da Configuração

Execute o script para verificar se as credenciais estão funcionando:

```bash
cd src/scripts
python conection_worksheets.py
```

## ⚠️ Segurança

- **NUNCA** commite o arquivo `credentials.json` no repositório
- Use variáveis de ambiente em produção
- Revogue e recrie as credenciais se forem expostas
- Monitore o uso das APIs no Google Cloud Console

## 🔧 Produção

Para produção, considere usar:

- Google Cloud Secret Manager
- AWS Secrets Manager
- Azure Key Vault
- Ou outro gerenciador de secrets
