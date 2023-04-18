# Makefile for building a Docker image locally and for GCP

# Docker image settings
IMAGE_NAME = sapientone
TAG = latest

# Google Cloud settings
GCP_PROJECT_ID = ${GOOGLE_PROJECT}
GCR_HOSTNAME = gcr.io
GCR_IMAGE_PATH = $(GCR_HOSTNAME)/$(GCP_PROJECT_ID)/$(IMAGE_NAME)

.PHONY: prepare-requirements build-local build-gcp push-gcp

prepare-requirements:
	poetry export -f requirements.txt --output requirements.txt

build: prepare-requirements
	docker build -t $(IMAGE_NAME):$(TAG) .

run--local:
	uvicorn sapientone.app:app --host 0.0.0.0 --port 8080 --reload

run--docker: build
	docker run \
		-p 8080:8080 \
		-e PGVECTOR_CONNECTION_STRING=${PGVECTOR_CONNECTION_STRING} \
		-e OPENAI_API_KEY=${OPENAI_API_KEY} \
		-e SAPIENTONE_API_KEY=${SAPIENTONE_API_KEY} \
		$(IMAGE_NAME):$(TAG)
