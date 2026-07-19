FROM nvcr.io/nvidia/pytorch@sha256:be06a21bd95a46bce1a5cfc0576051a40209f328440edaa2ba5cd35abf85ca1a

LABEL org.opencontainers.image.title="HRA bounded BioNeMo Recipes ESM-2 fixture"
LABEL io.hra.base.digest="sha256:be06a21bd95a46bce1a5cfc0576051a40209f328440edaa2ba5cd35abf85ca1a"
LABEL io.hra.model.revision="3674a6acb6c217bbeff709d182a11b196125dfc3"
LABEL io.hra.recipes.commit="66c150f2920d6155697d4edfc87289f239b65022"
LABEL io.hra.scope="bounded-fixture-only"

ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_DATASETS_OFFLINE=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    DO_NOT_TRACK=1 \
    TOKENIZERS_PARALLELISM=false \
    PYTHONNOUSERSITE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=0 \
    CUBLAS_WORKSPACE_CONFIG=:4096:8

WORKDIR /opt/hra

COPY artifact-lock.json code-review.json fixture.json plan.json requirements.lock runtime-review.json ./
COPY fetch_assets.py run_fixture.py verify_assets.py ./
COPY model ./model
COPY wheelhouse ./wheelhouse

RUN python verify_assets.py --root /opt/hra
RUN python -m venv --system-site-packages /opt/hra/venv \
    && PIP_CONSTRAINT= /opt/hra/venv/bin/python -m pip install \
       --no-index \
       --find-links=/opt/hra/wheelhouse \
       --require-hashes \
       --no-compile \
       -r /opt/hra/requirements.lock
RUN /opt/hra/venv/bin/python verify_assets.py --root /opt/hra --runtime
RUN rm -rf /opt/hra/wheelhouse

ENTRYPOINT ["/opt/hra/venv/bin/python", "/opt/hra/run_fixture.py"]
