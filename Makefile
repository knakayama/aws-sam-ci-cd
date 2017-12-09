SHELL = /usr/bin/env bash -xeo pipefail

STACK_NAME = aws-sam-ci-cd
AWS_ENV =
AWS_ARTIFACT_BUCKET =

build:
	@for target in $$(find src/handlers -maxdepth 2 -type f -name 'requirements.txt'); do \
		root_dir=$$PWD; \
		handler_dir=$$(dirname $$target); \
		handler=$$(basename $$handler_dir); \
		cd $$handler_dir; \
		docker image build --tag $(STACK_NAME)-$$handler .; \
		if [[ $$CIRCLECI == true ]]; then \
			docker container run -it --name $(STACK_NAME)-$$handler $(STACK_NAME)-$$handler; \
			docker container cp $(STACK_NAME)-$$handler:/workdir/vendored .; \
		else \
			docker container run \
				-it \
				--rm \
				--volume $$PWD/vendored:/workdir/vendored \
				$(STACK_NAME)-$$handler; \
		fi; \
		cd $$root_dir; \
	done

package:
	@aws cloudformation package \
		--template-file sam.yml \
		--s3-bucket $(AWS_ARTIFACT_BUCKET) \
		--output-template-file .sam/sam_packaged.yml

deploy:
	@if [[ $$CIRCLECI == true ]]; then \
		aws cloudformation deploy \
			--template-file .sam/sam_packaged.yml \
			--stack-name $(STACK_NAME) \
			--capabilities CAPABILITY_IAM \
			--parameter-overrides $$(cat params/$(AWS_ENV).ini | grep -vE '^#' | tr '\n' ' ' | awk '{print}') \
			--role-arn $$AWS_IAM_ROLE_CFN; \
	else \
		aws cloudformation deploy \
			--template-file .sam/sam_packaged.yml \
			--stack-name $(STACK_NAME) \
			--parameter-overrides $$(cat params/$(AWS_ENV).ini | grep -vE '^#' | tr '\n' ' ' | awk '{print}') \
			--capabilities CAPABILITY_IAM; \
	fi;
	@$(MAKE) output

output:
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--query 'Stacks[].Outputs' \
		--output table

localstack-up:
	@docker-compose up -d

localstack-stop:
	@docker-compose stop

install-all:
	@pip install -r requirements.txt -r requirements-dev.txt -c constraints.txt

install:
	@pip install -r requirements.txt -c constraints.txt

lint:
	@python -m flake8

test-sam:
	@aws cloudformation validate-template --template-body file://sam.yml

test-unit:
	@for target in $$(find src/handlers -maxdepth 2 -type d -name 'tests'); do \
		handler=$$(dirname $$target); \
		root_dir=$$PWD; \
		cd $$handler && \
			AWS_DEFAULT_REGION=ap-northeast-1 \
			AWS_SECRET_ACCESS_KEY=dummy \
			AWS_DEFAULT_REGION=dummy \
			python -m pytest tests; \
	done

test-e2e:
	@STACK_NAME=$(STACK_NAME) python -m pytest tests

all: build package deploy

.PHONY: \
	build \
	package \
	deploy \
	output \
	localstack-up \
	localstack-stop \
	test-unit \
	test-e2e \
	install-all \
	install \
	all
