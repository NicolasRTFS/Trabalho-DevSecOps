# AcervoHub - Descricao do Sistema

## Objetivo

AcervoHub simula uma aplicacao real de controle de acervo bibliografico para uma biblioteca pequena, escola, empresa ou centro cultural.

## Funcionalidades

O sistema oferece autenticacao, perfis `admin` e `leitor`, CRUD de usuarios por administradores, CRUD de livros, autores e categorias por administradores, consulta publica de catalogo e fluxo de emprestimo/devolucao para leitores autenticados.

## Tecnologias

FastAPI fornece a API HTTP. SQLAlchemy implementa ORM e consultas parametrizadas. PostgreSQL e o banco local via Docker Compose. JWT protege rotas autenticadas. Bcrypt armazena senhas com hash. Pytest executa testes automatizados.

## Arquitetura

A aplicacao e separada em `routes`, `services`, `schemas`, `models`, `auth`, `database` e `core`. Rotas validam entrada e delegam regras de negocio para servicos. O ORM acessa o banco por sessoes injetadas.

## Modelo de Dados

Tabelas: `users`, `authors`, `categories`, `books` e `loans`. Usuarios possuem papel, status ativo e hash de senha. Livros possuem ISBN unico, autor, categoria e quantidades. Emprestimos registram usuario, livro, datas e status.

## Relacionamentos

Um livro pertence a um autor e a uma categoria. Um emprestimo pertence a um usuario e a um livro. Um usuario pode ter varios emprestimos e um livro pode aparecer em varios emprestimos ao longo do tempo.

## Docker

`app` compila o backend e executa Uvicorn na porta `8000`. `postgres` executa PostgreSQL 16 em rede interna com volume persistente e healthcheck. O banco nao publica porta no host.

## Variaveis de Ambiente

`SECRET_KEY` assina tokens JWT. `DATABASE_URL` aponta para PostgreSQL. `CORS_ORIGINS` limita origens aceitas. `SEED_DATABASE` liga dados ficticios. `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` configuram o banco.

## Rotas Publicas

`GET /health`, `GET /books`, `GET /books/{id}`, `GET /authors`, `GET /categories`, `POST /auth/register` e `POST /auth/login`.

## Rotas Autenticadas

`GET /auth/me`, `POST /auth/logout`, `POST /loans`, `POST /loans/{id}/return` e `GET /me/loans`.

## Rotas Administrativas

`/admin/users`, `/admin/loans`, criacao/edicao/remocao de livros, autores e categorias exigem papel `admin`.

## Fluxo de Autenticacao

O usuario envia email e senha em `/auth/login`. A senha e comparada com hash bcrypt. Usuarios inativos nao autenticam. O token JWT deve ser enviado no header `Authorization: Bearer`.

## Fluxo de Usuarios

Administradores listam, criam, editam, ativam, desativam, alteram papel e removem usuarios. O sistema bloqueia a remocao, desativacao ou rebaixamento do ultimo admin ativo.

## Fluxo de Livros

Administradores cadastram livro com titulo, ISBN, ano, descricao, autor, categoria e quantidades. O sistema rejeita ISBN duplicado, quantidade negativa e disponibilidade acima do total.

## Fluxo de Emprestimos

Leitores autenticados solicitam emprestimo de livro disponivel. O sistema reduz a disponibilidade, registra data atual e vencimento em 14 dias. Na devolucao, marca como `devolvido`, registra data e aumenta a disponibilidade.

## Analise de Codigo

Ferramentas podem avaliar hash de senha, JWT, dependencias, validacoes Pydantic, protecoes de RBAC, bloqueio de acesso horizontal e uso de ORM.

## Analise de Infraestrutura

Ferramentas podem avaliar Dockerfile, usuario nao-root, healthchecks, rede propria, ausencia de porta publica do banco, variaveis de ambiente e volume persistente.

## Analise em Execucao

Com a aplicacao ativa, ferramentas podem testar rotas publicas, autenticadas e administrativas, CORS, headers basicos de seguranca, `/health`, regras de estoque e respostas de erro.

## Pipeline DevSecOps

O sistema alvo e acompanhado por uma esteira automatizada em `.github/workflows/devsecops.yml`. A pipeline executa testes, Secret Detection, SCA, SAST, IaC scanning, container scanning e DAST com OWASP ZAP. Os relatorios gerados sao armazenados como artefatos da execucao e tambem seguem a convencao de uso da pasta `reports/`.

A documentacao especifica da esteira esta em `docs/devsecops-pipeline.md`.
