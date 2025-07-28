import os
import subprocess
import json
import tempfile
import logging
import re
import sys
import pathlib

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def run_command(cmd):
    logger.info(f"Executing command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        logger.info(f"STDOUT:\n{result.stdout}")
        sys.stdout.flush()
    if result.stderr:
        logger.warning(f"STDERR:\n{result.stderr}")
        sys.stderr.flush()
    if result.returncode != 0:
        logger.error(f"Command error output:\n{result.stderr}")
        raise RuntimeError(f"Command failed (exit {result.returncode}): {result.stderr.strip()}")
    return result.stdout.strip()

def lambda_handler(event, context):
    try:
        repo_url = os.environ.get('GIT_REPO_URL')
        if not repo_url:
            raise ValueError("Missing required environment variable: GIT_REPO_URL")

        branch = os.environ.get('GIT_BRANCH', 'main')
        chart_dir = os.environ.get("CHART_DIR", "charts")
        chart_relative_path = os.environ.get("CHART_PATH", "charts/Chart.yaml")

        account_id = os.environ.get('AWS_ACCOUNT_ID')
        region = os.environ.get('AWS_REGION')
        ecr_repo = os.environ.get("ECR_REPO", "helm-chart-repo")

        if not account_id or not region:
            raise ValueError("Missing required environment variables: AWS_ACCOUNT_ID or AWS_REGION")

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            logger.info(f"Cloning branch '{branch}' from {repo_url}")
            run_command(f"git clone --depth 1 -b {branch} {repo_url} repo")
            os.chdir("repo")

            #chart_file = os.path.join("repo", chart_relative_path)
            chart_file = chart_relative_path
            
            logger.info(f"Chart file path {chart_file}")
            logger.info(f"Working directory: {os.getcwd()}")
            logger.info("Directory tree:")
            for path in pathlib.Path(".").rglob("*"):
                logger.info(str(path))

            if not os.path.exists(chart_file):
                raise FileNotFoundError(f"Expected Chart.yaml at: {chart_file}, but it was not found")
            
            with open(chart_file, "r") as f:
                content = f.read()

            version_line = next((line for line in content.splitlines() if line.startswith("version:")), None)
            if not version_line:
                raise ValueError("No version field found in Chart.yaml")

            current_version = version_line.split()[1]
            if not re.match(r'^\d+\.\d+\.\d+$', current_version):
                raise ValueError(f"Invalid semantic version: {current_version}")

            major, minor, patch = map(int, current_version.split("."))
            patch += 1
            new_version = f"{major}.{minor}.{patch}"

            logger.info(f"Upgrading chart version from {current_version} to {new_version}")
            content = content.replace(version_line, f"version: {new_version}")
            with open(chart_file, "w") as f:
                f.write(content)

            run_command(f"helm package {chart_file}")

            tgz_file = next((f for f in os.listdir(".") if f.endswith(".tgz")), None)
            if not tgz_file:
                raise FileNotFoundError("No .tgz package found after helm package")

            repo_uri = f"oci://{account_id}.dkr.ecr.{region}.amazonaws.com/"

            run_command(
                f"aws ecr get-login-password --region {region} | "
                f"helm registry login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
            )

            run_command(f"helm push {tgz_file} {repo_uri}")

        return {
            'statusCode': 200,
            'body': json.dumps(f"✅ Chart successfully pushed with version {new_version}")
        }

    except Exception as e:
        logger.error(f"❌ Lambda failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Lambda failed: {str(e)}")
        }
