#!/bin/bash
# Quick deployment script for Render

echo "🚀 Deploying TS-ErrorsAnalysis to Render..."

echo "📋 Step 1: Create render.yaml (already done ✓)"

echo ""
echo "📋 Step 2: Deploy to Render"
echo "   1. Go to: https://dashboard.render.com/select-repo"
echo "   2. Connect your GitHub: corzogac/TS-ErrorsAnalysis"
echo "   3. Select branch: claude/add-claude-documentation-d60DI"
echo "   4. Render will detect render.yaml and auto-configure!"
echo "   5. Click 'Apply'"

echo ""
echo "📋 Step 3: Deploy Frontend to Vercel"
echo "   1. Go to: https://vercel.com/new"
echo "   2. Import: corzogac/TS-ErrorsAnalysis"
echo "   3. Root Directory: frontend"
echo "   4. Environment Variables:"
echo "      VITE_API_URL=<your-render-backend-url>"
echo "   5. Deploy!"

echo ""
echo "🎯 Alternative: One-Command Deploy"
echo "   Click: https://render.com/deploy?repo=https://github.com/corzogac/TS-ErrorsAnalysis"

echo ""
echo "📚 Full instructions: See DEPLOYMENT.md"
