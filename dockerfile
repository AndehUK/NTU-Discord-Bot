FROM python:3.11.7-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV JISHAKU_NO_UNDERSCORE="true"
ENV JISHAKU_NO_DM_TRACEBACK="true"
ENV JISHAKU_HIDE="true"

CMD ["python3", "launcher.py"]