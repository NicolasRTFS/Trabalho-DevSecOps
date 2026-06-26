# AcervoHub

AcervoHub e uma API REST para gestao de acervo bibliografico de uma pequena biblioteca, escola, empresa ou centro cultural. Ela inclui autenticacao, perfis `admin` e `leitor`, CRUD de livros, autores, categorias, usuarios e fluxo de emprestimos.

## Tecnologias

FastAPI, SQLAlchemy, PostgreSQL, Docker, Docker Compose, JWT, bcrypt e pytest.

## Como executar

```bash
docker compose up --build
```

A API fica em `http://localhost:8000` e a documentacao interativa em `http://localhost:8000/docs`.

Opcionalmente, copie `.env.example` para `.env` antes de subir caso queira alterar segredos, CORS, credenciais ou seed.

Para parar e remover containers:

```bash
docker compose down
```

Para remover tambem o volume do banco:

```bash
docker compose down -v
```

## Servicos Docker

`app` executa a API FastAPI em usuario nao-root e expoe a porta `8000`. `postgres` executa PostgreSQL 16 com volume persistente e healthcheck. O banco nao e exposto para fora da rede Docker.

## Variaveis

Veja `.env.example`. Defina `SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, credenciais do PostgreSQL e `SEED_DATABASE`. O arquivo `.env` nao deve ser versionado.

## Dados ficticios

Ao iniciar com `SEED_DATABASE=true`, o sistema cria dados de exemplo:

- admin: `admin@example.com` / `Admin123!`
- leitor: `leitor@example.com` / `Leitor123!`
- 3 autores, 3 categorias, 8 livros e 2 emprestimos.

## Testes

```bash
pytest
```

Os testes usam SQLite temporario e cobrem cadastro, login, livros, bloqueios de permissao, usuarios, emprestimos, devolucao e `/health`.

## Pipeline DevSecOps

O projeto inclui uma esteira automatizada em `.github/workflows/devsecops.yml` para GitHub Actions. Ela executa:

- testes automatizados;
- Secret Detection com Gitleaks;
- SCA com pip-audit;
- SAST com Bandit e Semgrep;
- IaC scanning com Checkov;
- container scanning com Trivy;
- DAST com OWASP ZAP contra a aplicacao em execucao.

Os resultados sao publicados como artefatos da execucao e podem ser usados como evidencias no relatorio tecnico. A descricao completa esta em `docs/devsecops-pipeline.md`.

Um modelo de estrutura para o relatorio esta em `docs/report-template.md`.

Para checagens locais parciais:

```bash
chmod +x scripts/run-local-security-checks.sh
./scripts/run-local-security-checks.sh
```

## Endpoints principais

- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
- `GET /books`, `GET /books/{id}`, `POST /books`, `PUT /books/{id}`, `DELETE /books/{id}`
- `GET /authors`, `POST /authors`, `PUT /authors/{id}`, `DELETE /authors/{id}`
- `GET /categories`, `POST /categories`, `PUT /categories/{id}`, `DELETE /categories/{id}`
- `GET /me/loans`, `POST /loans`, `POST /loans/{id}/return`
- `GET /admin/users`, `POST /admin/users`, `PUT /admin/users/{id}`, `PATCH /admin/users/{id}/deactivate`
- `GET /admin/loans`, `GET /admin/loans/{id}`
- `GET /health`

## Exemplos com curl

Login:

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"Admin123!"}'
```

Listar livros:

```bash
curl http://localhost:8000/books
```

Criar livro como admin:

```bash
TOKEN="cole-o-token-aqui"
curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Novo Manual","isbn":"9780000000999","year":2024,"description":"Exemplo","author_id":1,"category_id":1,"total_quantity":2,"available_quantity":2}'
```

Solicitar emprestimo como leitor:

```bash
curl -X POST http://localhost:8000/loans \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"book_id":1}'
```

## Modulos

`app/models` contem entidades SQLAlchemy. `app/schemas` contem validacao Pydantic. `app/routes` expoe a API. `app/services` concentra regras de negocio. `app/auth` cuida de hash, JWT e dependencias de permissao. `app/database` configura a sessao.

## Relatorios

Ferramentas externas de SAST, DAST, analise de container ou dependencias podem salvar resultados em `reports/`. A pasta e ignorada pelo Git, exceto `reports/.gitkeep`.

Mais detalhes estao em `docs/system-description.md` e `docs/devsecops-pipeline.md`.
# Trabalho-DevSecOps
