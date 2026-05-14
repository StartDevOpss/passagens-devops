# 📄 GitHub Pages Setup Instructions

## Current Status
✅ Dashboard files are ready in the `docs/` folder
✅ All code is committed and pushed to GitHub
✅ CI/CD pipeline is configured

## To Enable GitHub Pages

Since GitHub Pages must be enabled through the repository settings (not via code), follow these steps:

### Steps to Enable:

1. **Go to your GitHub repository:**
   ```
   https://github.com/StartDevOpss/passagens-devops
   ```

2. **Navigate to Settings:**
   - Click on the "Settings" tab at the top of the repository

3. **Go to Pages section:**
   - In the left sidebar, click on "Pages"

4. **Configure the source:**
   - Under "Build and deployment"
   - Source: Select "Deploy from a branch"
   - Branch: Select "main"
   - Folder: Select "/docs"
   - Click "Save"

5. **Wait for deployment:**
   - GitHub will automatically deploy your site
   - It may take 1-2 minutes
   - You'll see a message: "Your site is live at https://startdevopss.github.io/passagens-devops/"

### Verify Deployment

Once enabled, your dashboard will be available at:
```
https://startdevopss.github.io/passagens-devops/
```

The dashboard will automatically:
- Load flight offers from `ofertas.json`
- Update every 30 seconds
- Display real-time statistics
- Show beautiful flight cards with pricing

## Alternative: GitHub Actions Workflow for Pages

If you prefer automated deployment via GitHub Actions, you can create `.github/workflows/pages.yml`:

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'docs'
      
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

However, the simpler approach is to just enable it in Settings as described above.

## Troubleshooting

**If the page doesn't load:**
- Check that the branch is "main" and folder is "/docs"
- Verify the files exist in the docs/ folder
- Wait a few minutes for the first deployment
- Check the Actions tab for any deployment errors

**If offers don't show:**
- The bot needs to be running to update `ofertas.json`
- Check that `ofertas.json` has valid data
- Open browser console (F12) to check for errors
