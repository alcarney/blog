FROM mcr.microsoft.com/devcontainers/base:noble

COPY tools.mk /

RUN su vscode -c "make -f tools.mk tools" \
    && rm tools.mk
