# Stage 1: Build helm + dependencies
FROM alpine:3.18 as helm-builder

ARG HELM_VERSION="v3.16.3"

RUN apk add --no-cache curl tar git unzip bash

WORKDIR /tmp

# Download and extract helm securely
RUN curl -sSL https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz && \
    tar -zxvf helm.tar.gz && \
    mv linux-amd64/helm /usr/local/bin/helm && \
    chmod +x /usr/local/bin/helm

# Stage 2: Final lambda image
FROM public.ecr.aws/lambda/python:3.9

# Install minimal dependencies for Git and AWS CLI
RUN yum install -y git unzip tar curl && yum clean all

# Copy Helm from builder stage
COPY --from=helm-builder /usr/local/bin/helm /usr/local/bin/helm

# Copy Lambda app
COPY app.py ./
COPY requirements.txt ./

# Install Python deps into Lambda root dir
RUN pip3 install -r requirements.txt -t .

CMD ["app.lambda_handler"]

