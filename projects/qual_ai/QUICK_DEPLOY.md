# Quick Deployment Reference

## 🚀 Fastest Way to Deploy

### Option 1: Docker Compose (Recommended for Testing)
```bash
cd projects/qual_ai
cp .env.example .env
# Edit .env with your GCP credentials
docker-compose up -d
```
✅ Access at `http://localhost:8000`

---

### Option 2: Google Cloud Run (Best for Production)
```bash
cd projects/qual_ai

# Set up credentials first
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy in one command
gcloud run deploy qual-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
✅ Gets public URL automatically

---

### Option 3: Interactive Deployment Script
```bash
cd projects/qual_ai
bash deploy.sh
```
✅ Choose from 6 deployment options

---

## 📋 Prerequisites by Deployment Method

| Method | Requirements |
|--------|--------------|
| Docker | `docker`, `docker-compose` |
| Cloud Run | GCP account, `gcloud` CLI |
| Local Dev | Python 3.9+, `pip` |
| VPS | SSH access, Ubuntu/Debian |

---

## 🔐 GCP Credentials Setup (Required for All Options)

```bash
# 1. Create service account
gcloud iam service-accounts create qual-ai-service

# 2. Grant Vertex AI permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:qual-ai-service@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/aiplatform.user

# 3. Create key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=qual-ai-service@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 4. Update .env
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/service-account-key.json
```

---

## 📊 Testing Deployment

```bash
# Health check
curl http://localhost:8000/health

# Agent info
curl http://localhost:8000/agent

# Test analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Sample interview transcript here",
    "data_type": "interview_transcript",
    "context": "User research study"
  }'
```

---

## 🐳 Docker Commands Cheat Sheet

```bash
# Build image
docker build -t qual-ai:latest .

# Run container
docker run -p 8000:8000 --env-file .env qual-ai:latest

# List running containers
docker ps

# View logs
docker logs -f CONTAINER_ID

# Stop container
docker stop CONTAINER_ID

# Remove image
docker rmi qual-ai:latest
```

---

## ☁️ Cloud Run Commands Cheat Sheet

```bash
# Deploy
gcloud run deploy qual-ai --source .

# View service URL
gcloud run services list

# View logs
gcloud run logs read qual-ai

# Update deployment
gcloud run deploy qual-ai --source .

# Delete service
gcloud run services delete qual-ai
```

---

## 📁 File Structure After Deployment

```
qual_ai/
├── agents.py                 # Core agent
├── app.py                   # FastAPI server
├── main.py                  # CLI entry point
├── Dockerfile               # Container image
├── docker-compose.yml       # Multi-container setup
├── requirements.txt         # Dependencies
├── DEPLOYMENT.md            # Full deployment guide
├── deploy.sh                # Interactive script
└── .env                     # Configuration (create from .env.example)
```

---

## 🔍 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs qual-ai

# Verify .env exists
ls -la .env

# Test credentials
cat $GOOGLE_APPLICATION_CREDENTIALS | head
```

### Port already in use
```bash
# Find what's using port 8000
lsof -i :8000

# Use different port
docker run -p 8080:8000 qual-ai:latest
```

### GCP authentication fails
```bash
# Verify credentials
gcloud auth application-default print-access-token

# Re-authenticate
gcloud auth login

# Set credentials explicitly
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Cloud Run (automatic)
gcloud run deploy qual-ai \
  --min-instances 1 \
  --max-instances 100

# Docker Compose
docker-compose up -d --scale qual-ai=3
```

### Resource Limits
```bash
# Cloud Run
gcloud run deploy qual-ai \
  --memory 2Gi \
  --cpu 2
```

---

## 🔒 Security Checklist

- [ ] Service account key stored securely
- [ ] Credentials not in version control
- [ ] Use `.env` file, never hardcode
- [ ] Enable IAM restrictions on service account
- [ ] Use Cloud Secret Manager for production
- [ ] Enable VPC connector for private deployments
- [ ] Set up firewall rules if needed
- [ ] Enable audit logging

---

## 💰 Cost Estimation

| Service | Tier | Monthly Cost |
|---------|------|-------------|
| Cloud Run | 1M requests/month | ~$5-20 |
| Docker locally | - | Free |
| Vertex AI API | per API call | Varies |

---

## 📚 Next Steps

1. **Local Testing**: `docker-compose up -d`
2. **Cloud Deployment**: `gcloud run deploy qual-ai --source .`
3. **Monitor**: `docker-compose logs -f` or `gcloud run logs read qual-ai`
4. **Scale**: Adjust replicas/resources as needed
5. **CI/CD**: Set up GitHub Actions (see `.github/workflows/`)

---

## 🆘 Getting Help

- **Docker Issues**: https://docs.docker.com/
- **Cloud Run**: https://cloud.google.com/run/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **GCP Auth**: https://cloud.google.com/docs/authentication

---

**Quick Deploy Summary**:
```bash
# 1. Setup credentials
export GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json

# 2. Deploy with Docker Compose
cd projects/qual_ai && docker-compose up -d

# 3. Access service
curl http://localhost:8000/health
```

That's it! 🎉
