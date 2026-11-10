FROM python:3.9-slim

WORKDIR /app

# Flask 라이브러리 설치
RUN pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org flask

# app.py 파일을 컨테이너 안으로 복사
COPY app.py .

# 5000번 포트 개방 및 Flask 실행
EXPOSE 5000
CMD ["python", "app.py"]