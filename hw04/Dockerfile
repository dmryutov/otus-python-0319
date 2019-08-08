FROM python:3.7-alpine

WORKDIR /app
COPY ./*.py ./

EXPOSE 8080
CMD ["python", "httpd.py", "--host=0.0.0.0", "--port=8000", "--workers=2", "--root=/www"]