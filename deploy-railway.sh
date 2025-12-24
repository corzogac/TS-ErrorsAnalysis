#!/bin/bash
# Quick deployment script for Railway

echo "🚀 Deploying TS-ErrorsAnalysis to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging in to Railway..."
railway login

# Initialize project
echo "🎯 Creating Railway project..."
railway init

# Link to GitHub repo (optional)
echo "🔗 Linking to GitHub..."
echo "Please link your GitHub repository in the Railway dashboard"

# Deploy backend
echo "🚂 Deploying backend..."
railway up

# Get backend URL
BACKEND_URL=$(railway domain)
echo "✅ Backend deployed to: $BACKEND_URL"

# Deploy frontend separately
echo "📱 To deploy frontend:"
echo "1. Go to https://vercel.com/new"
echo "2. Import your GitHub repository"
echo "3. Set Root Directory to: frontend"
echo "4. Set Environment Variable: VITE_API_URL=$BACKEND_URL"
echo "5. Deploy!"

echo ""
echo "🎉 Deployment initiated!"
echo "📊 Monitor deployment: https://railway.app/dashboard"
