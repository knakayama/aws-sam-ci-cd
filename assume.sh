#!/usr/bin/env bash

set -xeuo pipefail

ROLE_SESSION_NAME="$CIRCLE_USERNAME"
DURATION_SECONDS="900"

aws_sts_credentials="$(aws sts assume-role \
  --role-arn "$AWS_IAM_ROLE_CIRCLECI" \
  --role-session-name "$ROLE_SESSION_NAME" \
  --external-id "$AWS_IAM_ROLE_EXTERNAL_ID" \
  --duration-seconds "$DURATION_SECONDS" \
  --query "Credentials" \
  --output "json")"

cat <<EOT >> "envs.sh"
export AWS_ACCESS_KEY_ID="$(echo $aws_sts_credentials | jq -r '.AccessKeyId')"
export AWS_SECRET_ACCESS_KEY="$(echo $aws_sts_credentials | jq -r '.SecretAccessKey')"
export AWS_SESSION_TOKEN="$(echo $aws_sts_credentials | jq -r '.SessionToken')"
EOT
