# AWS Secrets Manager - Manual Setup Guide

Este documento explica como configurar secrets manualmente no AWS Secrets Manager após o Terraform criar a estrutura.

## Fluxo

```
Terraform Apply
  ├─ Cria caminho: app-name/environment/secret-name
  ├─ Cria recurso vazio (sem valor)
  └─ Output: ARN e instruções
       ↓
Developer/Admin
  ├─ Acessa AWS Console
  ├─ Localiza o secret pelo ARN
  ├─ Preenche o valor manualmente
  └─ Salva
       ↓
ECS Task
  ├─ Fetch secret from AWS Secrets Manager
  ├─ Injeta como environment variable
  └─ Aplicação usa o valor
```

## Padrão de Naming

Secrets são criados com o padrão:

```
{app-name}/{environment}/{secret-name}

Exemplo:
diagnostico-medico-api/prod/posthog_api_key
```

Benefícios:
- Organização clara por aplicação e ambiente
- Fácil descoberta no console
- Separação entre dev/staging/prod
- Suporta múltiplos secrets

## Step-by-Step: Preencher um Secret

### 1. Fazer Deploy com Terraform

```bash
cd terraform
terraform apply
```

Output mostrará os secrets criados:

```
Outputs:

secrets_arns = {
  "posthog_api_key" => {
    "arn"         = "arn:aws:secretsmanager:us-east-1:123456:secret:diagnostico-medico-api/prod/posthog_api_key-AbCdE"
    "env_var"     = "POSTHOG_API_KEY"
    "name"        = "diagnostico-medico-api/prod/posthog_api_key"
    "description" = "PostHog API Key for analytics"
  }
}
```

### 2. Acessar AWS Console

1. Acesse https://console.aws.amazon.com/secretsmanager
2. Selecione a região correta (ex: us-east-1)
3. Clique em **"All Secrets"** se não aparecer a lista

### 3. Localizar o Secret

Procure pelo nome: `diagnostico-medico-api/prod/posthog_api_key`

Ou filtre por ARN:
```
arn:aws:secretsmanager:us-east-1:123456:secret:diagnostico-medico-api/prod/posthog_api_key-*
```

### 4. Preencher o Valor

1. Clique no secret para abrir os detalhes
2. Procure pela seção **"Secret value"**
3. Clique em **"Retrieve secret value"** (será vazio)
4. Clique em **"Edit secret"** ou o botão de edição

**Método A: Plaintext**
```
POSTHOG_API_KEY: phx_sua_chave_real
```

**Método B: JSON (se múltiplos valores)**
```json
{
  "api_key": "phx_sua_chave_real",
  "endpoint": "https://us.posthog.com"
}
```

5. Clique **"Save"** ou **"Confirm"**

### 5. Verificar que Funcionou

```bash
# Testar acesso ao secret
aws secretsmanager get-secret-value \
  --secret-id "diagnostico-medico-api/prod/posthog_api_key" \
  --region us-east-1

# Output incluirá:
# {
#   "SecretString": "phx_sua_chave_real",
#   "Name": "diagnostico-medico-api/prod/posthog_api_key",
#   "ARN": "arn:aws:secretsmanager:..."
# }
```

### 6. Aplicação Lê Automaticamente

Na próxima vez que a ECS Task iniciar:
1. ECS Task Execution Role autentica no Secrets Manager
2. Fetch do valor secreto
3. Injeta como `POSTHOG_API_KEY` no container
4. Aplicação lê de `os.environ['POSTHOG_API_KEY']`

## Adicionar Novos Secrets

Para adicionar um novo secret à lista:

### 1. Atualizar Terraform

```hcl
# terraform/variables.tf
variable "secrets_to_create" {
  default = {
    "posthog_api_key" = {
      description        = "PostHog API Key for analytics"
      container_env_name = "POSTHOG_API_KEY"
    }
    "novo_secret" = {
      description        = "Descrição do novo secret"
      container_env_name = "NOVO_SECRET_ENV_VAR"
    }
  }
}
```

### 2. Apply no Terraform

```bash
cd terraform
terraform apply
```

Terraform criará:
- `diagnostico-medico-api/prod/novo_secret`

### 3. Preencher no AWS Console

Como descrito acima.

### 4. Atualizar Aplicação

Se a aplicação precisa usar a nova variável:

```python
# app/core/config.py
class Settings(BaseSettings):
    novo_secret: str = ""  # lê do env NOVO_SECRET_ENV_VAR
```

## Segurança

### ✅ Boas Práticas

1. **Nunca commit secrets** no git (mesmo que estejam em `.env`)
2. **Use IAM para controle de acesso**
   - Apenas ECS Task role tem permissão `secretsmanager:GetSecretValue`
   - Desenvolvedores têm acesso de leitura no Console apenas
3. **Auditoria ativada**
   - CloudTrail logs cada acesso ao secret
4. **Rotação automática** (opcional)
   - AWS Secrets Manager pode rotacionar automaticamente via Lambda
5. **Versionamento**
   - AWS mantém histórico de valores anteriores

### Revogar Acesso

Se um secret foi comprometido:

```bash
# 1. Criar nova versão com novo valor
aws secretsmanager put-secret-value \
  --secret-id "diagnostico-medico-api/prod/posthog_api_key" \
  --secret-string "phx_nova_chave"

# 2. Próxima task que iniciar usará novo valor
# (tasks existentes continuam com valor antigo até reiniciar)

# 3. Deletar secret antigo (opcional, após confirmar tudo)
aws secretsmanager delete-secret \
  --secret-id "diagnostico-medico-api/prod/posthog_api_key" \
  --recovery-window-in-days 7  # recuperável por 7 dias
```

## Troubleshooting

### Secret não aparece no console

```bash
# Listar secrets
aws secretsmanager list-secrets \
  --region us-east-1 \
  --filters Key=name,Values=diagnostico-medico-api

# Descrição completa
aws secretsmanager describe-secret \
  --secret-id "diagnostico-medico-api/prod/posthog_api_key" \
  --region us-east-1
```

### ECS Task não consegue ler o secret

```bash
# 1. Verificar permissão da IAM role
aws iam get-role-policy \
  --role-name diagnostico-medico-api-ecs-task-execution-role \
  --policy-name diagnostico-medico-api-ecs-task-execution-policy

# 2. Verificar que a Task Definition referencia o ARN correto
aws ecs describe-task-definition \
  --task-definition diagnostico-medico-api \
  --query 'taskDefinition.containerDefinitions[0].secrets'

# 3. Verificar logs da task
aws logs tail /ecs/diagnostico-medico-api --follow
```

### Erro: "ResourceNotFoundException"

A Task Definition está tentando acessar um secret que:
- Não existe
- ARN está errado
- Foi deletado

Solução:
```bash
# Confirmar que o secret existe
aws secretsmanager get-secret-value \
  --secret-id "arn:aws:secretsmanager:us-east-1:123456:secret:diagnostico-medico-api/prod/posthog_api_key-AbCdE"

# Se não existe, recriar via Terraform
cd terraform
terraform apply
```

## Variáveis de Ambiente

A aplicação lê automaticamente os secrets como env vars:

```python
import os

# ECS injeta POSTHOG_API_KEY automaticamente
posthog_key = os.environ.get('POSTHOG_API_KEY')

# Ou via Pydantic (como fazemos)
from app.core.config import Settings
settings = Settings()  # pydantic lê do env automaticamente
posthog_key = settings.posthog_api_key
```

## Monitorar Acessos

CloudTrail registra cada acesso:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=diagnostico-medico-api/prod/posthog_api_key \
  --region us-east-1 \
  --query 'Events[].{Time:EventTime,User:Username,Action:EventName}' \
  --output table
```

## Automação Futura

Você pode automatizar o preenchimento de secrets com:

**Lambda + EventBridge**
- Quando Terraform cria um secret vazio
- Lambda preenche o valor automaticamente
- Fonte: Parameter Store, Secrets Vault externo, etc.

**Git Secrets Scanning**
- GitHub detecta secrets em commits
- Webhook notifica para rotação

**SecretsSync Tool**
- Sincronizar secrets de um cofre central (Vault, 1Password)
- Para múltiplos ambientes e contas AWS

---

**Próximos Passos**

- [ ] Deploy com `terraform apply`
- [ ] Obter ARNs dos outputs
- [ ] Preencher secrets no AWS Console
- [ ] Testar com `aws secretsmanager get-secret-value`
- [ ] Reiniciar ECS tasks para aplicar secrets
- [ ] Verificar logs da aplicação
- [ ] Confirmar no PostHog que eventos estão chegando
