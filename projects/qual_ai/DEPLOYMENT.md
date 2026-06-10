# QUAL-AI Deployment Guide

Complete guide for deploying the QUAL-AI agent in various environments.

## Prerequisites

- Python 3.9+
- Google Cloud Platform (GCP) account with Vertex AI enabled
- Service account with Vertex AI credentials
- Docker (for containerized deployments)

## 1. Local Development

### Setup
```bash
# Clone repository
cd projects/qual_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up credentials
cp .env.example .env
# Edit .env with your GCP credentials
```

### Run Locally
```bash
# Option A: Direct execution
python main.py

# Option B: API server
python app.py
# Access at http://localhost:8000
```

---

## 2. Docker (Recommended for Production)

### Build Image
```bash
# Build Docker image
docker build -t qual-ai:latest .

# Or with specific tag
docker build -t qual-ai:v1.0.0 .
```

### Run Container
```bash
# Basic run
docker run -p 8000:8000 qual-ai:latest

# With environment file
docker run -p 8000:8000 --env-file .env qual-ai:latest

# With volume mounting for logs
docker run -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  qual-ai:latest

# Interactive mode
docker run -it -p 8000:8000 --env-file .env qual-ai:latest
```

### Using Docker Compose
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f qual-ai

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## 3. Google Cloud Run (Easiest)

### Prerequisites
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Deploy to Cloud Run
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Build and deploy
gcloud run deploy qual-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PORT=8000

# Or push to Artifact Registry first
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/qual-ai:latest
gcloud run deploy qual-ai \
  --image gcr.io/YOUR_PROJECT_ID/qual-ai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Configure Cloud Run Secrets
```bash
# Create secret for credentials
gcloud secrets create gcp-credentials --data-file=path/to/service-account-key.json

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding gcp-credentials \
  --member=serviceAccount:YOUR_PROJECT@appspot.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Deploy with secret
gcloud run deploy qual-ai \
  --update-secrets GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials:latest \
  --platform managed \
  --region us-central1
```

---

## 4. Google App Engine

### Setup
```bash
# Create app.yaml
cat > app.yaml << EOF
runtime: python311
env: standard
entrypoint: gunicorn -b :$PORT app:app

env_variables:
  PORT: "8000"
EOF
```

### Deploy
```bash
gcloud app deploy

# View logs
gcloud app logs read -f

# Visit
gcloud app browse
```

---

## 5. Kubernetes (Advanced)

### Create Kubernetes Manifests

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qual-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qual-ai
  template:
    metadata:
      labels:
        app: qual-ai
    spec:
      containers:
      - name: qual-ai
        image: gcr.io/YOUR_PROJECT_ID/qual-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/key.json
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: gcp-key
          mountPath: /var/secrets/google
      volumes:
      - name: gcp-key
        secret:
          secretName: gcp-credentials
---
apiVersion: v1
kind: Service
metadata:
  name: qual-ai-service
spec:
  type: LoadBalancer
  selector:
    app: qual-ai
  ports:
  - port: 80
    targetPort: 8000
```

### Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace qual-ai

# Create secret
kubectl create secret generic gcp-credentials \
  --from-file=key.json=path/to/service-account-key.json \
  -n qual-ai

# Deploy
kubectl apply -f deployment.yaml -n qual-ai

# Check status
kubectl get pods -n qual-ai
kubectl get service -n qual-ai

# View logs
kubectl logs -f deployment/qual-ai -n qual-ai

# Port forward
kubectl port-forward svc/qual-ai-service 8000:80 -n qual-ai
```

---

## 6. Heroku

### Prerequisites
```bash
npm install -g heroku
heroku login
```

### Create Heroku App
```bash
# Create app
heroku create qual-ai

# Set environment variables
heroku config:set GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Add GCP credentials to build
heroku config:set GCP_CREDENTIALS='{"type":"service_account",...}'
```

### Create Procfile
```bash
cat > Procfile << EOF
web: gunicorn -b :$PORT app:app
EOF
```

### Deploy
```bash
# Push to Heroku
git push heroku main

# View logs
heroku logs -f

# Visit
heroku open
```

---

## 7. Traditional VPS (DigitalOcean, AWS EC2, Linode)

### Setup Ubuntu/Debian Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3-pip python3-venv curl git

# Install Nginx
sudo apt install -y nginx

# Install Supervisor (process manager)
sudo apt install -y supervisor
```

### Deploy Application
```bash
# Clone repository
cd /home/ubuntu
git clone https://github.com/YOUR_REPO/portfolio.git
cd portfolio/projects/qual_ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
cp .env.example .env
# Edit with your credentials
```

### Configure Supervisor
```bash
# Create supervisor config
sudo tee /etc/supervisor/conf.d/qual-ai.conf > /dev/null << EOF
[program:qual-ai]
directory=/home/ubuntu/portfolio/projects/qual_ai
command=/home/ubuntu/portfolio/projects/qual_ai/venv/bin/gunicorn -b 127.0.0.1:8000 app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/qual-ai/err.log
stdout_logfile=/var/log/qual-ai/out.log
environment=PATH="/home/ubuntu/portfolio/projects/qual_ai/venv/bin"
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start qual-ai
```

### Configure Nginx Reverse Proxy
```bash
# Create Nginx config
sudo tee /etc/nginx/sites-available/qual-ai > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/qual-ai /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal check
sudo systemctl status certbot.timer
```

---

## 8. Environment Configuration

### .env File
```env
# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Server
PORT=8000
HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO

# Optional: Database (if adding persistence)
DATABASE_URL=postgresql://user:password@localhost:5432/qual_ai
```

---

## 9. Monitoring & Logging

### Application Monitoring
```bash
# Docker: Check logs
docker logs qual-ai

# Cloud Run: View logs
gcloud run logs read qual-ai

# Kubernetes: View logs
kubectl logs deployment/qual-ai -n qual-ai

# VPS: View supervisor logs
sudo tail -f /var/log/qual-ai/out.log
```

### Health Checks
All deployments use `/health` endpoint:
```bash
curl http://localhost:8000/health
```

---

## 10. Scaling & Performance

### Docker Compose (Multiple Instances)
```yaml
version: '3.8'
services:
  qual-ai-1:
    build: .
    ports:
      - "8001:8000"
  qual-ai-2:
    build: .
    ports:
      - "8002:8000"
  qual-ai-3:
    build: .
    ports:
      - "8003:8000"
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Kubernetes: Scale Replicas
```bash
kubectl scale deployment qual-ai --replicas=5 -n qual-ai
```

---

## Deployment Comparison

| Method | Difficulty | Cost | Scalability | Recommendation |
|--------|-----------|------|-------------|-----------------|
| Local | ⭐ | Free | None | Development |
| Docker | ⭐⭐ | Free | Limited | Testing |
| Cloud Run | ⭐⭐ | $ | ✅ High | Best for GCP |
| App Engine | ⭐⭐ | $ | ✅ Medium | Managed |
| Kubernetes | ⭐⭐⭐⭐ | $$$ | ✅ Very High | Enterprise |
| VPS | ⭐⭐ | $$ | ⚠️ Manual | Flexible |
| Heroku | ⭐ | $$ | ✅ Medium | Quick Start |

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs qual-ai

# Check environment
docker run -it --env-file .env qual-ai:latest /bin/bash
```

### Connection Issues
```bash
# Check service
curl http://localhost:8000/health

# Check port
lsof -i :8000
```

### GCP Authentication Errors
```bash
# Verify credentials
gcloud auth application-default print-access-token

# Set credentials explicitly
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

---

## CI/CD Integration

### GitHub Actions
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - uses: google-github-actions/setup-gcloud@v0
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      
      - run: |
          gcloud builds submit \
            --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/qual-ai:latest
      
      - run: |
          gcloud run deploy qual-ai \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/qual-ai:latest \
            --platform managed \
            --region us-central1
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] GCP credentials secured in secret manager
- [ ] Health checks passing
- [ ] Logs accessible and monitored
- [ ] Database connections tested (if applicable)
- [ ] SSL/TLS configured
- [ ] Rate limiting enabled
- [ ] Error handling implemented
- [ ] Performance tested under load
- [ ] Backup strategy defined
- [ ] Incident response plan documented
- [ ] Team trained on deployment

---

## Support

For issues, refer to:
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Docker Documentation](https://docs.docker.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
