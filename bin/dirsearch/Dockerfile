FROM python:3.14-slim

LABEL maintainer="maurosoria@protonmail.com"

ARG DIRSEARCH_STACK=async
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /opt/dirsearch
COPY . /opt/dirsearch/

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --only-binary=:all: -r requirements.txt -r requirements/db.txt \
    && if [ "$DIRSEARCH_STACK" = "native-rust" ]; then \
        apt-get update \
        && apt-get install -y --no-install-recommends build-essential ca-certificates curl \
        && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal \
        && . "$HOME/.cargo/env" \
        && python -m pip install --only-binary=:all: maturin \
        && python scripts/build_native.py --out dist/native-wheels \
        && python -m pip uninstall -y maturin \
        && rm -rf dist/native-wheels native/target "$HOME/.cargo" "$HOME/.rustup" \
        && apt-get purge -y --auto-remove build-essential curl \
        && rm -rf /var/lib/apt/lists/*; \
    fi \
    && python scripts/configure_stack.py config.ini "$DIRSEARCH_STACK" \
    && chmod +x dirsearch.py

ENTRYPOINT ["python", "dirsearch.py"]
CMD ["--help"]
