# Instructions to Fix Google Cloud Permissions

The issue we're facing is that the service account doesn't have the necessary permissions to access Google Cloud services. Here's how to fix it:

## 1. Access the Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Make sure you're in the project: `conference-cms-project`

## 2. Grant Permissions to Your Service Account

1. Navigate to **IAM & Admin** > **IAM** in the left sidebar
2. Find your service account: `drive-api-service-account@conference-cms-project.iam.gserviceaccount.com`
3. Click the pencil (edit) icon next to the service account
4. Click **ADD ANOTHER ROLE** and add the following roles:
   - **Storage Admin** (`roles/storage.admin`) - For GCS bucket management
   - **Firestore Admin** (`roles/datastore.owner`) - For Firestore database access
   - **Vertex AI User** (`roles/aiplatform.user`) - For AI services access
   - **Service Account User** (`roles/iam.serviceAccountUser`) - For general service account usage

5. Click **SAVE**

## 3. Enable Required APIs

Make sure the following APIs are enabled in your project:

1. Navigate to **APIs & Services** > **Library** in the left sidebar
2. Search for and enable each of these APIs:
   - Cloud Firestore API
   - Cloud Storage API
   - Vertex AI API
   - Google Drive API

To enable an API, click on it and then click the **ENABLE** button.

## 4. Create Firestore Database (if not exists)

If the Firestore database doesn't exist yet:

1. Navigate to **Firestore** in the left sidebar
2. Click **Create Database**
3. Choose **Native Mode**
4. Select a location (preferably the same as your GCS bucket)
5. Click **Create**

## 5. Once Permissions are Updated

After updating the permissions, restart your application with:

```bash
cd /Users/sowmithmandadi/dev/playground/drive-api
export GOOGLE_APPLICATION_CREDENTIALS="/Users/sowmithmandadi/dev/playground/drive-api/credentials.json"
python3 backend/run.py
```

Then test your application again using the same test document upload process. 