# CI/CD Pipeline - Guia de Uso

## Novo Pipeline Refatorado

O pipeline foi separado em **3 stages independentes** para maior flexibilidade:

```
┌─────────────────────────────────────────────────────┐
│          AUTOMÁTICO (em todo push/PR)               │
├─────────────────────────────────────────────────────┤
│  1. LINT   → verifica estilo e erros               │
│  2. TEST   → roda testes com cobertura             │
│  3. BUILD  → constrói imagem Docker (sem push)     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        MANUAL (workflow_dispatch via GitHub UI)     │
├─────────────────────────────────────────────────────┤
│  4. PUSH   → build + tag + push para ECR           │
│  5. DEPLOY → update ECS service (requer ECR)       │
└─────────────────────────────────────────────────────┘
```

## Fluxo de Trabalho

### 1️⃣ **Desenvolvimento Normal (Automático)**

```bash
git commit -m "fix: corrige bug"
git push origin feature-branch
```

**O que acontece automaticamente:**
- ✅ `lint` - ruff check + format
- ✅ `test` - pytest com cobertura
- ✅ `build` - docker build (local, sem enviar para lugar nenhum)

**Resultado:**
- ✅ Se passar: PR está pronto para merge
- ❌ Se falhar: feedback no PR para corrigir

---

### 2️⃣ **Pronto para Fazer Push para ECR**

Quando você quer fazer deploy (infraestrutura existe):

1. Vá até **Actions** no GitHub
2. Selecione **CI/CD Pipeline**
3. Clique em **Run workflow**
4. Escolha a branch (main recomendado)
5. Escolha **action**: `push` ou `full`
6. Clique **Run workflow**

```
┌──────────────────────────────────────────┐
│  Run workflow                            │
│                                          │
│  Branch: main                    ▼       │
│  Action: [push ▼]                        │
│          • push                          │
│          • deploy                        │
│          • full                          │
│                                          │
│  [Run workflow]                          │
└──────────────────────────────────────────┘
```

**O que acontece com `push`:**
- ✅ `build` - docker build
- ✅ `push` - AWS ECR Login + push das imagens
- ✅ Tags: `latest` e `<commit-hash>`

**Resultado:**
- ✅ Imagem está no ECR pronta para deploy
- ⚠️ Nenhum deployment automático ainda

---

### 3️⃣ **Fazer Deploy para ECS**

Depois que a imagem está no ECR:

1. **Actions** → **CI/CD Pipeline** → **Run workflow**
2. Branch: `main`
3. Action: `deploy` ou `full`
4. **Run workflow**

**O que acontece com `deploy`:**
- ✅ AWS credentials via OIDC
- ✅ Update ECS service com `force-new-deployment`
- ✅ Wait for services-stable (aguarda conclusão)

**Resultado:**
- ✅ Novo deploy rodando no ECS
- ✅ Aguarda até estar estável
- ✅ ALB começa a rotear para novas tasks

---

### 4️⃣ **Release Completa (Push + Deploy)**

Para fazer tudo de uma vez:

1. **Actions** → **CI/CD Pipeline** → **Run workflow**
2. Branch: `main`
3. Action: `full`
4. **Run workflow**

**O que acontece:**
- ✅ Build + Push ECR
- ✅ Deploy ECS
- ✅ Aguarda até estar estável

---

## Cenários Comuns

### 📌 Cenário 1: Destruir Infraestrutura para Economizar

```bash
# 1. Destrua a infra
terraform destroy

# 2. Seu PR é aprovado e mergeado normalmente
git merge feature/meu-feature

# 3. Push acontece:
# ✅ lint + test + build passam
# ❌ Nenhum push/deploy automático (sem infra, sem problema!)

# 4. Quando reconstruir a infra:
terraform apply

# 5. Faça push via workflow_dispatch
# GitHub Actions → CI/CD Pipeline → Run workflow → push
```

**Resultado:** PR não é bloqueado, build sempre funciona, deploy é opcional!

---

### 📌 Cenário 2: Ambiente de Staging Separado

Você pode ter múltiplos workflows ou usar diferentes secrets:

```bash
# Branch main → ECR prod, ECS prod
# Branch staging → ECR staging, ECS staging
```

Basta criar outro workflow `.github/workflows/deploy-staging.yml` com:
- Diferentes nomes de ECR_REPOSITORY
- Diferentes ECS_CLUSTER, ECS_SERVICE
- Triggers em `push` para branch staging

---

### 📌 Cenário 3: Hotfix Rápido

```bash
# 1. Merge hotfix
git merge hotfix/critical-bug

# 2. Automático: lint + test + build passam
# Seu merge não é bloqueado!

# 3. Quando estiver pronto para deploy:
# GitHub Actions → Run workflow → action: full
```

---

## Inputs do Workflow

| Input | Opções | Descrição |
|-------|--------|-----------|
| `action` | `push` \| `deploy` \| `full` | Qual stage executar |

- **`push`** - Build + Tag + Push ECR (sem deploy ECS)
- **`deploy`** - Deploy ECS (requer imagem já no ECR)
- **`full`** - Push ECR + Deploy ECS (release completa)

---

## Status dos Jobs

Veja os logs em **GitHub Actions**:

```
CI/CD Pipeline
├─ lint           ✅ passed (2m)
├─ test           ✅ passed (3m)
├─ build-image    ✅ passed (1m)
├─ push-to-ecr    ⏭️  skipped (não é workflow_dispatch)
└─ deploy-to-ecs  ⏭️  skipped (não é workflow_dispatch)
```

Quando você roda manual com `push`:
```
CI/CD Pipeline
├─ lint           ✅ passed (2m)
├─ test           ✅ passed (3m)
├─ build-image    ✅ passed (1m)
├─ push-to-ecr    ✅ passed (2m)     ← Executado!
└─ deploy-to-ecs  ⏭️  skipped
```

Quando você roda manual com `full`:
```
CI/CD Pipeline
├─ lint           ✅ passed (2m)
├─ test           ✅ passed (3m)
├─ build-image    ✅ passed (1m)
├─ push-to-ecr    ✅ passed (2m)
└─ deploy-to-ecs  ✅ passed (5m)     ← Executado!
```

---

## Segurança & Best Practices

### ✅ Boas Práticas

1. **Sempre faça PR antes de merge em main**
   - Lint + Test rodam automaticamente
   - Você vê se há problemas antes de mergear

2. **Use `full` apenas em branches principais**
   - `main` para produção
   - `staging` para staging (se houver)

3. **Monitore os logs**
   - GitHub Actions → seu workflow → see logs
   - Problemas no deploy? Veja o erro específico

4. **Teste localmente antes de push**
   ```bash
   pytest --cov=app
   ruff check .
   docker build -t diagnostico-medico-api:test .
   ```

### ⚠️ Cuidados

1. **Infra não existe?** Sem problema, build ainda funciona
   - Push/Deploy apenas quando infra estiver up
   
2. **Secrets AWS não configurados?** Deploy falhará
   - Configure `AWS_ROLE_TO_ASSUME` nos secrets do GitHub
   - Configure OIDC trust com GitHub Actions

3. **Múltiplos devs?** Coordene quem faz deploy
   - Evite 2 pessoas fazendo deploy simultâneo

---

## Troubleshooting

### ❌ "Push failed: ECR login error"

**Causa:** AWS credentials inválidos ou OIDC não configurado

**Solução:**
1. Verifique `AWS_ROLE_TO_ASSUME` nos secrets GitHub
2. Configure OIDC trust: `terraform/github-actions.tf`
3. Role deve ter permissão ECR

### ❌ "Deploy failed: ECS service not found"

**Causa:** Infraestrutura foi destruída ou nome do serviço errado

**Solução:**
1. Verifique se ECS cluster/service existem: `aws ecs list-services`
2. Recrie com terraform: `terraform apply`

### ❌ "Build failed: Test error"

**Causa:** Erro no código

**Solução:**
1. Veja logs no GitHub Actions
2. Rode localmente: `pytest --cov=app`
3. Corrija o código
4. Novo commit + push

---

## Sumário Rápido

| Ação | Como Fazer | Resultado |
|------|-----------|-----------|
| **Dev normal** | `git push` | lint + test + build ✅ |
| **Push ECR** | Workflow → `push` | docker push ✅ |
| **Deploy ECS** | Workflow → `deploy` | ECS update ✅ |
| **Release total** | Workflow → `full` | push + deploy ✅ |
| **Sem infra** | Merge normalmente | Build funciona, deploy opcional |

---

**Última atualização:** 22 de Junho de 2026 | Pipeline v2.0
