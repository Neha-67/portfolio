# Deploy QUAL-AI from Cloud Only (No Downloads)

**Deploy directly from GitHub using only Google Cloud Console - no local setup needed!**

---

## 🌐 **Method 1: Deploy via Cloud Console (Easiest)**

### **Step 1: Go to Google Cloud Console**
Open this link in your browser:
```
https://console.cloud.google.com/
```

### **Step 2: Create a New Project**

1. Click on the project dropdown (top left)
2. Click **"NEW PROJECT"**
3. Enter name: `qual-ai-project`
4. Click **CREATE**
5. Wait for project to be created
6. Click the notification to select it

### **Step 3: Enable Required APIs**

1. In the search bar at top, search: `Cloud Run API`
2. Click it → Click **ENABLE**
3. Search again: `Artifact Registry API`
4. Click it → Click **ENABLE**
5. Search again: `Vertex AI API`
6. Click it → Click **ENABLE**

### **Step 4: Connect GitHub**

1. Go to: https://console.cloud.google.com/run
2. Click **CREATE SERVICE**
3. Select **"Deploy from source code"**
4. Choose **GitHub** as source
5. Click **SET UP WITH CLOUD BUILD**
6. Authorize GitHub (click through prompts)
7. Select your repository: `portfolio`
8. Select branch: `main`
9. Select directory: `projects/qual_ai`

### **Step 5: Configure Deployment**

1. **Service name**: `qual-ai`
2. **Region**: `us-central1`
3. **Memory**: `512 MB`
4. **CPU**: `1`
5. **Allow unauthenticated access**: ✅ Check this
6. Click **DEPLOY**

### **Step 6: Wait for Deployment**

- Takes 2-5 minutes
- You'll see a blue checkmark when done
- Your service URL will appear (copy it!)

### **Step 7: Test Your Service**

1. Copy the service URL from the success message
2. Open it in a new tab: `https://qual-ai-xxxxx.run.app`
3. Add `/docs` to the end to see the API
4. Add `/health` to test it's working

---

## ☁️ **Method 2: Deploy via Cloud Shell (Even Faster)**

### **Step 1: Open Cloud Shell**

1. Go to: https://console.cloud.google.com
2. Click the **terminal icon** (top right) → Opens Cloud Shell
3. A terminal appears at the bottom

### **Step 2: Set Your Project**

```bash
# List projects
gcloud projects list

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### **Step 3: Clone and Deploy**

```bash
# Clone your repository
git clone https://github.com/Neha-67/portfolio.git
cd portfolio/projects/qual_ai

# Enable APIs
gcloud services enable run.googleapis.com aiplatform.googleapis.com

# Deploy
gcloud run deploy qual-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### **Step 4: Get Your URL**

```bash
gcloud run services describe qual-ai --format='value(status.url)'
```

Copy the URL and open it in a browser! 🎉

---

## 🔑 **Create Service Account (Cloud Console Only)**

If you need GCP credentials for the agent:

### **Step 1: Open IAM & Admin**

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **CREATE SERVICE ACCOUNT**
3. Name: `qual-ai-service`
4. Click **CREATE AND CONTINUE**

### **Step 2: Grant Permissions**

1. Click **Grant this service account access to project**
2. Add role: **Vertex AI User**
3. Click **CONTINUE** → **DONE**

### **Step 3: Create Key**

1. Click the service account you just created
2. Go to **KEYS** tab
3. Click **ADD KEY** → **Create new key**
4. Choose **JSON**
5. Click **CREATE**
6. File downloads automatically

### **Step 4: Use the Key**

Option A: Upload to Cloud Run as secret
```bash
# In Cloud Shell:
gcloud secrets create gcp-credentials \
  --data-file=path/to/your/downloaded/key.json

gcloud run deploy qual-ai \
  --update-secrets GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials:latest
```

Option B: Use in `.env` file (commit to repo)
1. Download key from console
2. Copy contents to your `.env` file
3. Commit to GitHub
4. Redeploy

---

## 🎯 **Quickest Path (Copy-Paste)**

### **In Cloud Shell, run:**

```bash
# Set your project (replace YOUR_PROJECT_ID)
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com aiplatform.googleapis.com

# Clone and deploy
git clone https://github.com/Neha-67/portfolio.git
cd portfolio/projects/qual_ai
gcloud run deploy qual-ai --source . --platform managed --region us-central1 --allow-unauthenticated

# Get URL
gcloud run services describe qual-ai --format='value(status.url)'
```

**Done!** ✅

---

## 📊 **What Happens After Deployment**

After you click deploy or run the command:

1. **Google Cloud builds your code** (2-3 min)
2. **Creates Docker container** automatically
3. **Deploys to Cloud Run** (global infrastructure)
4. **Gives you a public HTTPS URL** 🔒
5. **Service is immediately live**

---

## 🔍 **Monitor from Console**

### **View Logs:**
1. Go to: https://console.cloud.google.com/run
2. Click on `qual-ai` service
3. Click **LOGS** tab
4. See real-time logs

### **View Metrics:**
1. Click **METRICS** tab
2. See requests, errors, latency

### **View Revisions:**
1. Click **REVISIONS** tab
2. See deployment history
3. Can rollback if needed

---

## 🚀 **Deploy Updates**

To deploy new changes:

**Option 1: Using GitHub Connection (Auto-deploy)**
```bash
# Just push to GitHub
git push origin main
# Cloud Build automatically redeploys!
```

**Option 2: Manual Redeploy from Console**
1. Go to Cloud Run
2. Click `qual-ai`
3. Click **EDIT & DEPLOY NEW REVISION**
4. Click **DEPLOY**

**Option 3: From Cloud Shell**
```bash
cd portfolio/projects/qual_ai
gcloud run deploy qual-ai --source .
```

---

## 💾 **Save Your URLs**

After deployment, save these:

```
Service URL: https://qual-ai-xxxxx-us-central1.a.run.app
API Docs: https://qual-ai-xxxxx-us-central1.a.run.app/docs
Health Check: https://qual-ai-xxxxx-us-central1.a.run.app/health
```

---

## ❌ **Troubleshooting**

### **Problem: "Authorization failed"**
- Make sure you're logged in: `gcloud auth login`
- In Cloud Console, verify you're in correct project (top-left dropdown)

### **Problem: "Service not found"**
- Wait 30 seconds after deployment completes
- Refresh the page
- Check Cloud Run services list

### **Problem: API not enabled**
- Go to: https://console.cloud.google.com/apis/dashboard
- Search for the API
- Click **ENABLE**

### **Problem: Can't see deployment progress**
- Go to: https://console.cloud.google.com/cloud-build/builds
- See all builds in progress

---

## 📱 **Access Your Agent Anywhere**

Once deployed, your QUAL-AI is:
- ✅ Live on the internet
- ✅ HTTPS/SSL encrypted
- ✅ Auto-scaling
- ✅ Globally available
- ✅ No server to manage

Share the URL: `https://qual-ai-xxxxx-us-central1.a.run.app`

---

## 🎉 **You're Done!**

No downloads needed. Everything happens in the cloud! 

### **Next Steps:**
1. Open your service URL in browser
2. Click `/docs` to see API
3. Try sending data to `/analyze` endpoint
4. Monitor with `/health` checks

---

## 📚 **Useful Links**

- **Google Cloud Console**: https://console.cloud.google.com
- **Cloud Run Dashboard**: https://console.cloud.google.com/run
- **Your Repository**: https://github.com/Neha-67/portfolio

---

**That's it! Deploy in under 5 minutes with zero local setup! 🚀**
