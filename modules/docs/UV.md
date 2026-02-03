## O que é o uv
uv é uma ferramenta moderna e rápida da Astral para gerenciar projetos e dependências Python. Ele substitui fluxos comuns de pip/venv e cria um ambiente reprodutível a partir do pyproject.toml e do arquivo de lock.

## Comandos principais
- uv init: inicia um novo projeto e cria o pyproject.toml
- uv add <pacote>: adiciona dependências e atualiza o lock
- uv remove <pacote>: remove dependências e atualiza o lock
- uv lock: resolve e gera o arquivo de lock
- uv sync: sincroniza o ambiente com o lock
- uv run <comando>: executa um comando usando o ambiente do projeto
- uv pip <args>: compatibilidade com comandos do pip
- uv venv: cria um ambiente virtual
