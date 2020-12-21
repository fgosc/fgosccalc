.PHONY: build
.PHONY: deploy deploy-prod
.PHONY: app-deploy-staging app-deploy-production
.PHONY: pre-deploy post-deploy
.PHONY: sync
.PHONY: docker-build docker-run docker-deploy

build:
	npm run build

deploy: pre-deploy app-deploy-staging post-deploy

deploy-prod: pre-deploy app-deploy-production post-deploy

app-deploy-staging:
	gcloud app deploy --no-promote -v stg

app-deploy-production:
	gcloud app deploy

pre-deploy: build
	python3 makeprop.py
	mv requirements.txt requirements-backup.txt
	mv requirements-gcloud.txt requirements.txt

post-deploy:
	mv requirements.txt requirements-gcloud.txt
	mv requirements-backup.txt requirements.txt

sync:
	git checkout master
	git fetch origin --prune
	git merge origin/master --ff
	git submodule update --remote

docker-build:
	docker build -t fgosc/fgosccalc:latest .

docker-run:
	docker run --rm -it -p 18080:8080 fgosc/fgosccalc:latest

docker-deploy:
	gcloud builds submit --tag gcr.io/fgosccalc/fgosccalc
	gcloud run deploy --image gcr.io/fgosccalc/fgosccalc --platform managed
