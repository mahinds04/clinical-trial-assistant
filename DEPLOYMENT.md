# Streamlit Deployment Guide

This guide explains how to deploy the Clinical Trial Assistant to Streamlit Cloud and other platforms.

## 🚀 Quick Start for Streamlit Cloud

1. **Fork/Clone this repository** to your GitHub account

2. **Sign up for Streamlit Cloud** at https://streamlit.io/cloud

3. **Connect your GitHub repository** in Streamlit Cloud

4. **Configure the app** in Streamlit Cloud:
   - Main file path: `app.py` (or `streamlit_app.py`)
   - Python version: 3.11 (or latest)
   - Requirements file: `requirements_deployment.txt`

5. **Optional: Set environment variables**:
   ```
   DEPLOYMENT_ENV=cloud
   HUGGINGFACE_API_KEY=your_key_here (optional for enhanced AI features)
   ```

6. **Deploy** - Click "Deploy" and Streamlit Cloud will automatically build your app

The app will work immediately with the included demo dataset!

## 📋 Deployment Options Summary

| Option | Ease | Cost | Performance | Full AI Features |
|--------|------|------|-------------|------------------|
| **Streamlit Cloud** | ⭐⭐⭐⭐⭐ | Free | Good | Optional |
| **Docker** | ⭐⭐⭐ | Varies | Excellent | Yes |
| **Heroku** | ⭐⭐⭐⭐ | Free tier | Good | Optional |
| **Railway** | ⭐⭐⭐⭐ | Free tier | Good | Optional |

## Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements_deployment.txt

# Run the app
streamlit run app.py
```

## Alternative Deployment Options

### Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker build -t clinical-trial-assistant .

# Run the container
docker run -p 8501:8501 clinical-trial-assistant
```

### Heroku Deployment

1. Create a `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Set the buildpack:
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Dockerfile
3. Set environment variables if needed
4. Deploy

## Configuration

### Environment Variables

- `DEPLOYMENT_ENV`: Set to `cloud` for cloud deployment, `local` for local with Ollama
- `HUGGINGFACE_API_KEY`: Optional, for HuggingFace model access
- `DEMO_SAMPLE_SIZE`: Number of trials in demo dataset (default: 5000)

### Data Requirements

The app includes a demo dataset (`data/clin_trials_demo.csv`) for immediate functionality. For production use:

1. Replace with your full clinical trials dataset
2. Run the indexer to create the vector database:
   ```bash
   python -m src.indexer.create_index
   ```

## Features

- **Interactive Chat Interface**: Ask questions about clinical trials
- **Trial Explorer**: Browse and filter available trials
- **Responsive Design**: Works on desktop and mobile
- **Graceful Fallbacks**: Works with or without full AI capabilities

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **No Trials Found**: Check that the demo data file exists in `data/clin_trials_demo.csv`
3. **Slow Response**: The demo uses simple keyword search, full version needs vector database

### Performance Optimization

- Use the demo dataset for faster deployment
- Consider using HuggingFace Inference API for model hosting
- Enable Streamlit's caching for better performance

## Security Notes

- Never commit API keys to the repository
- Use environment variables for sensitive configuration
- The demo runs locally without external API calls for privacy

## Support

For issues or questions:
1. Check the main README.md
2. Review the error messages in the Streamlit interface
3. Open an issue on the GitHub repository