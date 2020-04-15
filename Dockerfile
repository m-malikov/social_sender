FROM python:3.8.2-slim
COPY . .
RUN pip install -r requirements.txt
CMD python social_sender.py