FROM python:3

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py generate_ticket_link.py"]

# Setup nginx
RUN echo "server {server_name <DOMAIN_NAME>;  location / {  proxy_pass http://localhost:8000;}}" >> /etc/nginx/sites-enabled/ticket