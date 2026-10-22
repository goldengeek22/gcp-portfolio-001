# env.sh
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
export REGION=europe-west1            # change to any region you prefer
export REPO=portfolio-001                 # Artifact Registry repo name
export IMAGE=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/tasks-api
