#!/bin/bash

# QUAL-AI Quick Deployment Script
set -e

echo "🚀 QUAL-AI Deployment Helper"
echo "=============================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not installed. Please install: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose found"
echo ""

# Menu
echo "Choose deployment method:"
echo "1) Local Development"
echo "2) Docker (Development)"
echo "3) Docker Compose (Production)"
echo "4) Google Cloud Run"
echo "5) Setup GCP Credentials"
echo "6) View Logs"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo "🔧 Setting up local development..."
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        echo ""
        echo "✓ Setup complete!"
        echo "📝 Next steps:"
        echo "  1. source venv/bin/activate"
        echo "  2. cp .env.example .env"
        echo "  3. Edit .env with your GCP credentials"
        echo "  4. python app.py"
        ;;
        
    2)
        echo "🐳 Building Docker image..."
        docker build -t qual-ai:latest .
        echo ""
        echo "✓ Image built successfully!"
        echo "📝 Run with:"
        echo "  docker run -p 8000:8000 --env-file .env qual-ai:latest"
        ;;
        
    3)
        echo "🚀 Starting Docker Compose..."
        cp .env.example .env
        echo "⚠️  Edit .env with your GCP credentials before proceeding!"
        read -p "Press Enter once you've updated .env..."
        docker-compose up -d
        echo ""
        echo "✓ Services started!"
        echo "📊 Access at http://localhost:8000"
        echo "📝 View logs with: docker-compose logs -f"
        ;;
        
    4)
        echo "☁️  Deploying to Google Cloud Run..."
        
        if ! command -v gcloud &> /dev/null; then
            echo "❌ gcloud CLI not installed"
            echo "Install from: https://cloud.google.com/sdk/docs/install"
            exit 1
        fi
        
        read -p "Enter GCP Project ID: " project_id
        read -p "Enter Cloud Run region (default: us-central1): " region
        region=${region:-us-central1}
        
        echo "Setting up..."
        gcloud config set project $project_id
        gcloud services enable run.googleapis.com
        
        echo "Building and pushing image..."
        gcloud run deploy qual-ai \
            --source . \
            --platform managed \
            --region $region \
            --allow-unauthenticated
        
        echo ""
        echo "✓ Deployment complete!"
        gcloud run services list --platform managed
        ;;
        
    5)
        echo "🔐 Google Cloud Credentials Setup"
        echo ""
        echo "Steps:"
        echo "1. Go to: https://console.cloud.google.com/apis/credentials"
        echo "2. Click 'Create Credentials' → 'Service Account'"
        echo "3. Fill in service account details"
        echo "4. Grant 'Vertex AI User' role"
        echo "5. Create JSON key"
        echo "6. Download the key file"
        echo "7. Run: cp /path/to/key.json ./service-account-key.json"
        echo ""
        read -p "Press Enter once credentials are set up..."
        
        if [ -f "./service-account-key.json" ]; then
            echo "✓ Credentials found!"
            echo "Add to .env: GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json"
        else
            echo "⚠️  service-account-key.json not found in current directory"
        fi
        ;;
        
    6)
        echo "📊 View Logs"
        echo ""
        echo "1) Docker Compose logs"
        echo "2) Specific container"
        echo "3) Cloud Run logs"
        echo ""
        read -p "Choose (1-3): " log_choice
        
        case $log_choice in
            1)
                docker-compose logs -f
                ;;
            2)
                docker ps
                read -p "Enter container name/ID: " container
                docker logs -f $container
                ;;
            3)
                read -p "Enter service name (default: qual-ai): " service
                service=${service:-qual-ai}
                gcloud run logs read $service
                ;;
            *)
                echo "Invalid choice"
                ;;
        esac
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
