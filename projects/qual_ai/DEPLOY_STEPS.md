# QUAL-AI Deployment: Step-by-Step Guide

**Follow these steps to deploy your QUAL-AI agent in 10-15 minutes.**

---

## ⚡ **QUICKEST PATH: Deploy to Cloud Run (5-10 minutes)**

### **Step 1: Install Google Cloud SDK**

```bash
# On macOS
brew install google-cloud-sdk

# On Ubuntu/Debian
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# On Windows
# Download from: https://cloud.google.com/sdk/docs/install-sdk#windows

# Verify installation
gcloud --version
```

### **Step 2: Authenticate with Google Cloud**

```bash
# Login to your Google account
gcloud auth login

# This will open a browser window - click "Allow"
```

### **Step 3: Set Your GCP Project**

```bash
# List available projects
gcloud projects list

# Set the project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Example:
# gcloud config set project my-ai-project-123
```

### **Step 4: Enable Required APIs**

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API (for Docker images)
gcloud services enable artifactregistry.googleapis.com

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### **Step 5: Create GCP Service Account**

```bash
# Create service account
gcloud iam service-accounts create qual-ai-service \
  --display-name="QUAL-AI Service Account"

# Grant Vertex AI permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:qual-ai-service@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/aiplatform.user

# Create key file
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=qual-ai-service@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Verify the file was created
ls -la service-account-key.json
```

### **Step 6: Set Environment Variables**

```bash
# Navigate to qual_ai folder
cd projects/qual_ai

# Copy example .env file
cp .env.example .env

# Add credentials to .env
echo "GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/service-account-key.json" >> .env

# Verify .env was updated
cat .env
```

### **Step 7: Deploy to Cloud Run**

```bash
# Make sure you're in the qual_ai directory
cd /workspaces/portfolio/projects/qual_ai

# Deploy (this command does everything!)
gcloud run deploy qual-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600
```

**This will:**
- Build the Docker image
- Push it to Google Container Registry
- Deploy to Cloud Run
- Give you a public URL

### **Step 8: Get Your Deployment URL**

```bash
# The URL will be displayed after deployment
# Or get it with:
gcloud run services describe qual-ai --format='value(status.url)'

# Output will look like:
# https://qual-ai-XXXXX-us-central1.a.run.app
```

### **Step 9: Test Your Deployment**

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe qual-ai --format='value(status.url)')

# Test health check
curl $SERVICE_URL/health

# Get agent info
curl $SERVICE_URL/agent

# View interactive API docs
echo "Open in browser: $SERVICE_URL/docs"
```

### **Step 10: Send Your First Analysis Request**

```bash
SERVICE_URL=$(gcloud run services describe qual-ai --format='value(status.url)')

curl -X POST $SERVICE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data": "User mentioned they struggle with payment failures and reliability issues. Another user complained about lack of new features. The first user thinks reliability is more important.",
    "data_type": "interview_transcript",
    "context": "User research on digital payments"
  }'
```

---

## ✅ **You're Done!**

Your QUAL-AI agent is now live at: **`https://qual-ai-XXXXX-us-central1.a.run.app`**

---

## 📚 Alternative: Deploy Locally with Docker

If you prefer local testing first:

### **Step 1: Install Docker**

```bash
# macOS
brew install docker

# Ubuntu/Debian
sudo apt-get install docker.io

# Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
```

### **Step 2: Start Docker**

```bash
# On macOS/Windows: Open Docker Desktop

# On Linux
sudo systemctl start docker
```

### **Step 3: Navigate to Project**

```bash
cd projects/qual_ai
cp .env.example .env
# Edit .env with your Google credentials if you have them
```

### **Step 4: Build Docker Image**

```bash
docker build -t qual-ai:latest .
```

### **Step 5: Run Container**

```bash
docker run -p 8000:8000 qual-ai:latest
```

### **Step 6: Access Your Agent**

```bash
# Health check
curl http://localhost:8000/health

# View API docs
# Open in browser: http://localhost:8000/docs

# Test analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Your interview data here",
    "data_type": "interview_transcript"
  }'
```

---

## 🆘 Troubleshooting

### **Problem: `gcloud` command not found**

```bash
# Add to PATH
export PATH="$PATH:$HOME/google-cloud-sdk/bin"

# Or reinstall
curl https://sdk.cloud.google.com | bash
```

### **Problem: Authentication failed**

```bash
# Re-authenticate
gcloud auth login

# Check current authentication
gcloud auth list

# Set active account
gcloud config set account YOUR_EMAIL
```

### **Problem: Project not set**

```bash
# List projects
gcloud projects list

# Set project
gcloud config set project PROJECT_ID

# Verify
gcloud config get-value project
```

### **Problem: Deployment failed with "permission denied"**

```bash
# Check IAM roles
gcloud projects get-iam-policy YOUR_PROJECT_ID

# Grant Cloud Run admin role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:qual-ai-service@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.developer
```

### **Problem: Service account key not found**

```bash
# Recreate the key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=qual-ai-service@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Update .env
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/service-account-key.json
```

### **Problem: Port 8000 already in use**

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
docker run -p 8001:8000 qual-ai:latest
```

---

## 📊 Deployment Status Check

```bash
# Check Cloud Run service status
gcloud run services list

# View recent deployments
gcloud run revisions list --service=qual-ai

# View logs
gcloud run logs read qual-ai --limit 50

# View real-time logs
gcloud run logs read qual-ai --follow
```

---

## 🔒 Secure Your Deployment

### **Restrict Access (Make it private)**

```bash
# Only allow authenticated users
gcloud run deploy qual-ai \
  --no-allow-unauthenticated \
  --update-secrets GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials:latest
```

### **Add API Key for public access**

```bash
# Create API key
gcloud alpha services api-keys create --api-target="run.googleapis.com"

# Use in requests
curl -H "X-API-Key: YOUR_API_KEY" https://qual-ai-xxx.run.app/health
```

---

## 💰 Monitor Costs

```bash
# View current billing
gcloud billing accounts list

# Set spending alerts
# Go to: https://console.cloud.google.com/billing/alerts

# Estimate: Cloud Run costs ~$0.00001667 per request
# 1M requests/month ≈ $5-20 depending on memory
```

---

## 📈 Next Steps After Deployment

1. **Monitor Logs**
   ```bash
   gcloud run logs read qual-ai --follow
   ```

2. **Update Your Code**
   ```bash
   # Make changes locally, then:
   gcloud run deploy qual-ai --source .
   ```

3. **Scale Up**
   ```bash
   gcloud run deploy qual-ai \
     --min-instances 1 \
     --max-instances 100
   ```

4. **Set up CI/CD**
   - GitHub Actions will auto-deploy on push
   - See: `.github/workflows/deploy-qual-ai.yml`

---

## 🎯 Quick Commands Reference

```bash
# Deploy
gcloud run deploy qual-ai --source . --platform managed --region us-central1

# Get URL
gcloud run services describe qual-ai --format='value(status.url)'

# View logs
gcloud run logs read qual-ai

# Delete service
gcloud run services delete qual-ai

# Build locally
docker build -t qual-ai:latest .

# Run locally
docker run -p 8000:8000 qual-ai:latest
```

---

## 🎉 Success Indicators

After deployment, you should see:

✅ `gcloud run deploy` completes with a service URL
✅ `curl https://qual-ai-xxx.run.app/health` returns `{"status":"healthy"}`
✅ `curl https://qual-ai-xxx.run.app/agent` returns agent information
✅ `/docs` shows interactive API documentation

---

## 📞 Need Help?

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Cloud Run Guide**: https://cloud.google.com/run/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Docker Guide**: https://docs.docker.com/

---

**That's it! Your QUAL-AI agent will be live in 5-10 minutes! 🚀**
