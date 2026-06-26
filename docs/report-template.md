# Modelo de Relatorio Tecnico - AcervoHub DevSecOps

## 1. Descricao do Sistema e Ferramental

Sistema alvo: AcervoHub, API REST de gestao de acervo bibliografico.

Stack: FastAPI, SQLAlchemy, PostgreSQL, Docker, Docker Compose, JWT, bcrypt e pytest.

Pipeline: GitHub Actions em `.github/workflows/devsecops.yml`.

Ferramentas:

- Gitleaks para Secret Detection.
- pip-audit para SCA.
- Bandit e Semgrep para SAST.
- Checkov para IaC scanning.
- Trivy para container scanning.
- OWASP ZAP para DAST.

## 2. Evidencias de Execucao

Anexar capturas ou logs da aba Actions contendo:

- status da execucao da pipeline;
- artefato `code-security-reports`;
- artefato `infrastructure-security-reports`;
- artefato `dast-security-reports`;
- execucao local de testes, quando aplicavel.

## 3. Analise de Falsos Positivos e Alertas Irrelevantes

Para cada ferramenta, registrar:

- alerta encontrado;
- arquivo ou endpoint afetado;
- classificacao da ferramenta;
- motivo para considerar falso positivo, risco aceito ou alerta irrelevante.

Exemplo: usuarios e senhas de seed em README e `.env.example` sao credenciais ficticias para ambiente local, nao segredos reais de producao.

## 4. Identificacao e Correcao de Falhas Reais

Para cada falha real:

- ferramenta que detectou;
- evidencia do achado;
- impacto no AcervoHub;
- severidade;
- correcao aplicada ou proposta;
- validacao apos a correcao.

## 5. Analise Critica dos Resultados

Discutir:

- cobertura da pipeline;
- diferenca entre SAST, SCA, IaC e DAST;
- limitacoes do ZAP baseline;
- pontos em que revisao manual ainda e necessaria;
- melhorias futuras, como DAST autenticado, SBOM, assinatura de imagem e gates por severidade.
