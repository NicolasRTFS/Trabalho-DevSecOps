# Pipeline DevSecOps do AcervoHub

## Objetivo

Esta esteira automatizada transforma o AcervoHub no sistema alvo de uma avaliacao DevSecOps. O pipeline varre codigo-fonte, dependencias, infraestrutura Docker e aplicacao em execucao, gerando evidencias para o relatorio tecnico.

## Plataforma

A implementacao principal esta em `.github/workflows/devsecops.yml` e foi planejada para GitHub Actions. O arquivo executa em `push`, `pull_request` e tambem manualmente por `workflow_dispatch`.

## Etapas obrigatorias

### Secret Detection

Ferramenta: Gitleaks executado via container Docker.

Objetivo: procurar credenciais, chaves de API, tokens e segredos acidentalmente versionados no repositorio e no historico de commits.

Evidencia esperada: `gitleaks.json`.

### SCA - Software Composition Analysis

Ferramenta: pip-audit.

Objetivo: analisar `requirements.txt` em busca de vulnerabilidades conhecidas nas bibliotecas Python.

Evidencia esperada: `pip-audit.json`.

### SAST - Static Application Security Testing

Ferramentas: Bandit e Semgrep.

Objetivo: analisar o codigo Python em busca de padroes inseguros, problemas de autenticacao, validacao, uso de criptografia, SQL injection, exposicao de erro e outras classes relacionadas ao OWASP Top 10.

Evidencias esperadas: `bandit.json` e `semgrep.json`.

### IaC Scanning

Ferramenta: Checkov.

Objetivo: avaliar `Dockerfile` e `docker-compose.yml`, incluindo usuario do container, exposicao de portas, configuracoes sensiveis, healthchecks e praticas de infraestrutura.

Evidencia esperada: `checkov.json`.

### Container Scanning

Ferramenta: Trivy executado via container Docker.

Objetivo: analisar a imagem Docker do AcervoHub em busca de vulnerabilidades de sistema operacional e bibliotecas empacotadas.

Evidencia esperada: `trivy-image.json`.

### DAST - Dynamic Application Security Testing

Ferramenta: OWASP ZAP Baseline Scan executado via container Docker.

Objetivo: subir a aplicacao com Docker Compose e executar uma varredura dinamica contra `http://localhost:8000`, avaliando headers, configuracoes HTTP, exposicoes e comportamentos exploraveis em tempo de execucao.

Evidencias esperadas: `zap-baseline.html` e `zap-baseline.json`.

## Como executar no GitHub

1. Suba o projeto para um repositorio GitHub.
2. Verifique se Actions esta habilitado no repositorio.
3. Acesse a aba `Actions`.
4. Selecione `AcervoHub DevSecOps Pipeline`.
5. Execute manualmente com `Run workflow` ou faca um `push`.
6. Abra a execucao concluida e baixe os artefatos:
   - `code-security-reports`
   - `infrastructure-security-reports`
   - `dast-security-reports`

## Como executar checagens locais

Para uma verificacao local parcial:

```bash
chmod +x scripts/run-local-security-checks.sh
./scripts/run-local-security-checks.sh
```

O script executa testes e, quando as ferramentas estao instaladas, gera relatorios em `reports/`.

## Como usar no relatorio tecnico

Use os artefatos da pipeline como evidencias. O relatorio deve distinguir:

- falhas reais, com impacto e correcao proposta;
- falsos positivos ou alertas aceitaveis no contexto;
- limitacoes das ferramentas;
- diferenca entre analise estatica, analise de dependencia, infraestrutura e DAST.

Um roteiro de relatorio esta disponivel em `docs/report-template.md`.

## Observacoes para analise critica

Alguns alertas podem ser esperados em ambiente de desenvolvimento. Por exemplo, credenciais de seed em `.env.example` e no README sao dados ficticios documentados para uso local, nao segredos reais. Mesmo assim, o relatorio deve explicar por que esses achados nao representam uma credencial produtiva.

O DAST usa uma varredura baseline, portanto ele identifica problemas comuns de configuracao e exposicao HTTP, mas nao substitui testes autenticados profundos nem revisao manual de regras de negocio.
