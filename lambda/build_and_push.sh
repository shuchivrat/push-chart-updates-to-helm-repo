#!/bin/bash
set -euo pipefail

AWS_ACCOUNT_ID="$1"
AWS_REGION="us-east-1"
REPO_NAME="lambda-helm"
APP_FILE="app.py"

# Compute MD5 hash of the file
if [ ! -f "$APP_FILE" ]; then
  echo "Error: $APP_FILE not found."
  exit 1
fi

# md5sum works on Linux; use md5 on macOS
IMAGE_TAG=$(md5sum "$APP_FILE" | awk '{ print $1 }')  # Linux
# IMAGE_TAG=$(md5 -q "$APP_FILE")  # macOS alternative

echo "Computed image tag (MD5): $IMAGE_TAG"

aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker build -t $REPO_NAME .
docker tag $REPO_NAME:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"
