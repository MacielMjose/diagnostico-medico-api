#!/usr/bin/env bash
#
# Restaura secrets do AWS Secrets Manager agendados para deleção e os importa
# (se necessário) no state do Terraform.
#
# Resolve o erro:
#   "InvalidRequestException: You can't create this secret because a secret
#   with this name is already scheduled for deletion."
# e também o cenário:
#   "ResourceExistsException: ... secret ... already exists" (quando o secret
#   existe na AWS mas não está no state do Terraform).
#
# Idempotente: pode ser rodado quantas vezes quiser sem causar erro.
#
# USO (dentro do Git Bash):
#   ./restore-import-secrets.sh
#   ./restore-import-secrets.sh ../infra
#
set -uo pipefail

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO: ajuste o prefixo/ambiente, região e a lista de secrets
# ---------------------------------------------------------------------------
SECRET_PREFIX="diagnostico-medico-api/dev"
SECRET_KEYS=("posthog_api_key" "groq_api_key")
AWS_REGION="us-east-1"

TERRAFORM_DIR="${1:-.}"

echo "==> Diretorio do Terraform: $TERRAFORM_DIR"
cd "$TERRAFORM_DIR" || { echo "[ERRO] Nao foi possivel acessar '$TERRAFORM_DIR'"; exit 1; }

for key in "${SECRET_KEYS[@]}"; do
    secret_id="${SECRET_PREFIX}/${key}"
    resource_address="aws_secretsmanager_secret.app_secrets[\"${key}\"]"

    echo ""
    echo "=== Processando: ${secret_id} ==="

    # -------------------------------------------------------------------
    # 1. Verificar se o secret está agendado para deleção e restaurar
    # -------------------------------------------------------------------
    describe_output=$(aws secretsmanager describe-secret --secret-id "$secret_id" --region "$AWS_REGION" 2>&1)
    describe_exit_code=$?

    if [ $describe_exit_code -ne 0 ]; then
        echo "  [AVISO] Secret '${secret_id}' nao encontrado ou erro ao consultar. Pulando restore/import."
        echo "  Detalhe do erro AWS CLI:"
        echo "  $describe_output"
        continue
    fi

    deleted_date=$(echo "$describe_output" | grep -o '"DeletedDate":[^,}]*' || true)

    if [ -n "$deleted_date" ]; then
        echo "  Secret agendado para delecao. Restaurando..."
        if aws secretsmanager restore-secret --secret-id "$secret_id" --region "$AWS_REGION" >/dev/null 2>&1; then
            echo "  Restaurado com sucesso."
        else
            echo "  [ERRO] Falha ao restaurar '${secret_id}'."
            continue
        fi
    else
        echo "  Secret ja esta ativo (sem DeletedDate). Nenhum restore necessario."
    fi

    # -------------------------------------------------------------------
    # 2. Verificar se já está no state do Terraform
    # -------------------------------------------------------------------
    if terraform state show "$resource_address" >/dev/null 2>&1; then
        echo "  Ja presente no state do Terraform. Nenhum import necessario."
        continue
    fi

    # -------------------------------------------------------------------
    # 3. Importar no state
    # -------------------------------------------------------------------
    echo "  Nao esta no state. Importando..."
    if terraform import "$resource_address" "$secret_id"; then
        echo "  Import concluido com sucesso."
    else
        echo "  [ERRO] Falha ao importar '${resource_address}'."
    fi
done

echo ""
echo "==> Concluido. Rode 'terraform plan' para conferir se nao ha diffs inesperados."
