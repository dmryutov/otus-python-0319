FROM jupyter/minimal-notebook

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on

COPY ./requirements.txt .
RUN pip install --no-cache-dir -q -r requirements.txt

WORKDIR /app
COPY . .

EXPOSE 8888