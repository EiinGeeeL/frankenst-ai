FROM python:3.12.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	STREAMLIT_SERVER_HEADLESS=true \
	STREAMLIT_SERVER_PORT=8501 \
	STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

RUN apt-get update -y && \
	apt-get install -y --no-install-recommends \
		curl \
		ca-certificates \
		unixodbc && \
	curl -fsSL https://astral.sh/uv/install.sh | sh && \
	apt-get purge -y --auto-remove curl && \
	rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:/home/.local/bin:$PATH"

COPY requirements*.txt /tmp/requirements/
RUN uv pip install --system --no-cache -r /tmp/requirements/requirements.txt \
    && rm -rf /tmp/requirements

COPY . /app
RUN uv pip install --system -e .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]