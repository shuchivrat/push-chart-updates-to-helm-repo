# --- Stage 1: Build helm + dependencies ---
FROM alpine:3.18 as helm-builder

ARG HELM_VERSION="v3.16.3"

RUN apk add --no-cache curl tar git unzip bash

WORKDIR /tmp

# Download and extract Helm securely
RUN curl -sSL https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz && \
    tar -zxvf helm.tar.gz && \
    mv linux-amd64/helm /usr/local/bin/helm && \
    chmod +x /usr/local/bin/helm

# --- Stage 2: Final Lambda image ---
FROM public.ecr.aws/lambda/python:3.9

# Install Git, curl, tar, unzip, and AWS CLI v2
RUN yum install -y git curl unzip tar && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip && \
    yum clean all

# Copy Helm binary from builder stage
COPY --from=helm-builder /usr/local/bin/helm /usr/local/bin/helm

# Copy Python app and dependencies
COPY app.py ./
COPY requirements.txt ./

RUN chmod 644 app.py

# Install Python dependencies into Lambda runtime
RUN pip3 install -r requirements.txt -t .

# Define entrypoint
CMD ["app.lambda_handler"]

