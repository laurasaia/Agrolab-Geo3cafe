FROM python:3.12-slim

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /campo_vertentes

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY campo_vertentes/ ./campo_vertentes/

RUN uv sync --frozen

ENV APP_PORT=8765
ENV SOLARA_APP_TITLE="Geo3Café"
ENV SOLARA_MODE=development
ENV SOLARA_THEME_SHOW_BANNER=False
ENV PYTHONPATH=/campo_vertentes

EXPOSE 8765

CMD ["sh", "-c", "if [ \"$SOLARA_MODE\" = \"production\" ]; then exec uv run solara run campo_vertentes.pages --host=0.0.0.0 --port=${APP_PORT} --production --no-open --workers 1; else exec uv run solara run campo_vertentes.pages --host=0.0.0.0 --port=${APP_PORT}; fi"]

# COPY pyproject.toml ./
# COPY campo_vertentes/ ./campo_vertentes

# ARG INSTALL_MODE=dev
# RUN if [ "$INSTALL_MODE" = "prod" ]; then \
# 		pip install --no-cache-dir .; \
# 	else \
# 		pip install --no-cache-dir -e .; \
# 	fi

# ENV APP_PORT=8765
# ENV SOLARA_MODE=development

# EXPOSE 8765
# CMD ["sh", "-c", "if [ \"$SOLARA_MODE\" = \"production\" ]; then exec solara run campo_vertentes.pages --host=0.0.0.0 --port=${APP_PORT} --production --no-open --workers 1; else exec solara run campo_vertentes.pages --host=0.0.0.0 --port=${APP_PORT}; fi"]
