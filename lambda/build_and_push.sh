#!/bin/bash
set -euo pipefail

AWS_ACCOUNT_ID="$1"
AWS_REGION="us-east-1"
REPO_NAME="lambda-helm"

aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker build -t $REPO_NAME .
docker tag $REPO_NAME:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest"
