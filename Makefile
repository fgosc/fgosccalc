.PHONY: build
.PHONY: deploy deploy-prod
.PHONY: app-deploy-staging app-deploy-production
.PHONY: pre-deploy post-deploy

build:
	npm run build

deploy: pre-deploy app-deploy-staging post-deploy

deploy-prod: pre-deploy app-deploy-production post-deploy

app-deploy-staging:
	gcloud app deploy --no-promote

app-deploy-production:
	gcloud app deploy

pre-deploy:
	python3 makeprop.py
	mv requirements.txt requirements-backup.txt
	mv requirements-gcloud.txt requirements.txt

post-deploy:
	mv requirements.txt requirements-gcloud.txt
	mv requirements-backup.txt requirements.txt
