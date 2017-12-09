#!/usr/bin/env bash

set -xeo pipefail

REGEX_RELEASE_TAG="v([0-9]+\.){2}[0-9]+"

if [[ "$CIRCLE_TAG" =~ $REGEX_RELEASE_TAG ]]; then
  aws_account_id="$AWS_ACCOUNT_ID_PRD"
  aws_env="prd"
  aws_artifact_bucket="$AWS_ARTIFACT_BUCKET_PRD"
else
  aws_account_id="$AWS_ACCOUNT_ID_DEV"
  aws_env="dev"
  aws_artifact_bucket="$AWS_ARTIFACT_BUCKET_DEV"
fi

cat <<EOT > "envs.sh"
export AWS_ACCOUNT_ID="$aws_account_id"
export AWS_ENV="$aws_env"
export AWS_DEFAULT_REGION="ap-northeast-1"
export AWS_ARTIFACT_BUCKET="$aws_artifact_bucket"
export AWS_IAM_ROLE_CIRCLECI="arn:aws:iam::${aws_account_id}:role/circleci-role"
export AWS_IAM_ROLE_CFN="arn:aws:iam::${aws_account_id}:role/cfn-role"
EOT
