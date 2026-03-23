# Geo3Café

Infraestrutura e Desenvolvimento da Plataforma Geo3Café

Este repositório centraliza toda a stack tecnológica da plataforma Geo3Café, uma solução de geovisualização e colaboração voltada ao monitoramento do cultivo de café. Como um Monorepo, ele gerencia desde a camada de dados geoespaciais até as interfaces reativas e APIs de integração.

# Estrutura do Projeto

apps/api/: Backend REST em FastAPI (Python) que processa a lógica de negócio.

apps/campo-vertentes/: Frontend reativo em Solara (Python) focado em dashboards e mapas.

infra/: Arquivos de infraestrutura Docker (compose).

geoserver_data/: Configurações de serviço, workspaces e estilos do GeoServer.

# Pré-requisitos (Desenvolvimento)

WSL2 (Ubuntu 22.04+): Melhora compatibilidade com Docker para usuários Windows.

Docker: Orquestração de todos os serviços (GeoServer, FastAPI, Solara e MongoDB).

IDE recomendada: VS Code com as extensões WSL, Python, Ruff e Mypy instaladas.

Gerenciador de Pacotes: Recomendamos o uv para gerenciar dependências e grupos de desenvolvimento.

# Configuração Rápida (Onboarding)

1. Clonar e Preparar Dados
    ```Bash
    git clone https://github.com/seu-usuario/geo3cafe.git
    cd geo3cafe
    ```
    **IMPORTANTE (Dados do GeoServer):** Adicione a camada de dados do geoserver em ./geoserver_data/data/.
2. Ambiente e Dependências
    ```Bash
    cp .env.example .env
    uv sync --group dev  # Instala as ferramentas de qualidade (Ruff/Ty)
    ```
3. Subir a Stack Docker
    O Docker orquestra todos os serviços da plataforma:

    ```Bash
    docker compose -f infra/docker-compose.yml up --env-file .env --build
    ```
4. Popular o Banco de Dados (Primeira execução)
    ```Bash
    docker compose -f infra/docker-compose.yml exec -T mongo mongorestore --db geo3cafe_db <caminho_para_dump>
    ```

# Acessos Locais (Endpoints)

Serviço | URL | Descrição
--------|-----|----------
Geo3Café App | http://localhost:8765 | Interface Solara
API Docs | http://localhost:8000/docs | Swagger FastAPI
GeoServer | http://localhost:8080/geoserver | Painel (admin/geoserver)

# Automação no VS Code

O arquivo .vscode/settings.json está configurado para:

- Ruff: Formatação e organização de imports automática ao salvar (Ctrl+S).
- Ty: Validação de tipos estáticos para garantir segurança em operações geoespaciais.

## Verificação Manual
Execute para corrigir erros comuns e formatar o código:

```Bash
# Formata e corrige erros comuns via Ruff
uv run ruff check . --fix
uv run ruff format .

# Verifica integridade de tipos via Ty
uv ty check .
```