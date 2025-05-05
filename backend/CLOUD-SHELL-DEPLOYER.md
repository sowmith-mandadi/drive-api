# App Engine Deployment Guide

This guide explains how to deploy the backend to Google App Engine, including how to resolve common permission issues.

## Prerequisites

- Google Cloud Platform account with billing enabled
- App Engine enabled in your project
- Appropriate permissions to deploy to App Engine

## Permission Requirements

To deploy to App Engine, you need the following roles:
- **App Engine Deployer** (`roles/appengine.deployer`) - Required to deploy applications
- **App Engine Service Admin** (`roles/appengine.serviceAdmin`) - Required to create/update services
- **Storage Object Admin** (`roles/storage.objectAdmin`) - Required for deployment artifacts

## Resolving Permission Issues

If you see a permission error like:
```
ERROR: (gcloud.app.deploy) Permissions error fetching application [apps/YOUR-PROJECT-ID].
Please make sure that you have permission to view applications on the project and that
YOUR-EMAIL has the App Engine Deployer (roles/appengine.deployer) role.
```

### Option 1: Request permissions from project owner

Ask the project owner to grant you the necessary permissions:

```bash
# Add App Engine Deployer role
gcloud projects add-iam-policy-binding PROJECT-ID \
    --member="user:YOUR-EMAIL" \
    --role="roles/appengine.deployer"

# Add App Engine Service Admin role
gcloud projects add-iam-policy-binding PROJECT-ID \
    --member="user:YOUR-EMAIL" \
    --role="roles/appengine.serviceAdmin"

# Add Storage Object Admin role
gcloud projects add-iam-policy-binding PROJECT-ID \
    --member="user:YOUR-EMAIL" \
    --role="roles/storage.objectAdmin"
```

### Option 2: Create and deploy to your own project

If you have full control over your own project:

1. Create a new project in the Google Cloud Console
2. Enable App Engine API in the new project
3. Configure gcloud to use your project:
   ```bash
   gcloud config set project YOUR-NEW-PROJECT-ID
   ```

## Deployment Steps

Once permissions are resolved:

```bash
# Set your GCP project
export PROJECT_ID=$(gcloud config get-value project)
echo "Using project: $PROJECT_ID"

# Generate a secure session key
export SESSION_SECRET_KEY=$(openssl rand -hex 32)

# Deploy the application to App Engine
gcloud app deploy app.yaml \
  --project=$PROJECT_ID \
  --set-env-vars="SESSION_SECRET_KEY=${SESSION_SECRET_KEY},GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
```

If you have Google OAuth credentials, add them to the deployment command:

```bash
gcloud app deploy app.yaml \
  --project=$PROJECT_ID \
  --set-env-vars="SESSION_SECRET_KEY=${SESSION_SECRET_KEY},GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLIENT_ID=YOUR-CLIENT-ID,GOOGLE_CLIENT_SECRET=YOUR-CLIENT-SECRET"
```

## Creating GCS Bucket (Optional)

```bash
# Create a storage bucket for uploads
gsutil mb -p $PROJECT_ID -l us-central1 gs://${PROJECT_ID}-uploads

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

gsutil lifecycle set lifecycle.json gs://${PROJECT_ID}-uploads
rm lifecycle.json
```

## After Deployment

Your application will be available at:
```
https://PROJECT-ID.uc.r.appspot.com
```

To view logs:
```bash
gcloud app logs tail -s default
```
