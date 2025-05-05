# Deploying the Backend in Google Cloud Shell

This guide explains how to use the `backend-deploy.zip` file to deploy your application in Google Cloud Shell.

## Prerequisites

- Google Cloud Platform account with billing enabled
- App Engine enabled in your project
- Appropriate permissions to deploy to App Engine

## Deployment Steps

### 1. Upload the ZIP File

1. Open [Google Cloud Shell](https://shell.cloud.google.com/)
2. Click the three-dot menu and select "Upload"
3. Choose `backend-deploy.zip` from your local machine
4. Wait for the upload to complete

### 2. Extract and Set Up

```bash
# Extract the ZIP file
unzip backend-deploy.zip

# Navigate to the extracted directory
cd temp_deploy

# Make the setup script executable (if needed)
chmod +x run_cloud_shell.sh

# Run the setup script
./run_cloud_shell.sh
```

The script will:
- Create a virtual environment
- Install all required dependencies
- Detect your Python version and use compatible packages
- Set up upload directories
- Start the development server to test

### 3. Deploy to App Engine

Once you've verified everything works in the development server, follow these steps to deploy to App Engine:

```bash
# Stop the development server (Ctrl+C)

# Set your GCP project (replace YOUR-PROJECT-ID with your actual project ID)
gcloud config set project YOUR-PROJECT-ID

# Generate a secure session key (required for deployment)
SESSION_SECRET_KEY=$(openssl rand -hex 32)

# Deploy the application to App Engine with environment variables
gcloud app deploy app.yaml \
  --project=YOUR-PROJECT-ID \
  --set-env-vars="SESSION_SECRET_KEY=${SESSION_SECRET_KEY}"
```

If you have Google OAuth credentials, add them to the deployment command:

```bash
gcloud app deploy app.yaml \
  --project=YOUR-PROJECT-ID \
  --set-env-vars="SESSION_SECRET_KEY=${SESSION_SECRET_KEY},GOOGLE_CLIENT_ID=YOUR-CLIENT-ID,GOOGLE_CLIENT_SECRET=YOUR-CLIENT-SECRET"
```

### 4. Create GCS Bucket (Optional)

If you want to use Google Cloud Storage for file uploads:

```bash
# Create a storage bucket
gsutil mb -p YOUR-PROJECT-ID -l us-central1 gs://YOUR-PROJECT-ID-uploads

# Set lifecycle policy to auto-delete temp files after 1 day
echo '{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 1,
          "matchPrefix": ["uploads/temp/"]
        }
      }
    ]
  }
}' > lifecycle.json

gsutil lifecycle set lifecycle.json gs://YOUR-PROJECT-ID-uploads
rm lifecycle.json
```

### 5. View Your Deployed App

After deployment completes, you can view your application at:

```
https://YOUR-PROJECT-ID.uc.r.appspot.com
```

### Troubleshooting

- If you encounter package compatibility issues, check the script outputs and error messages
- For Python 3.12+, the script will automatically patch `config.py` for compatibility
- If deployment fails, check the logs using `gcloud app logs tail`
- If you didn't set OAuth credentials, the app will use stub implementations for some features
