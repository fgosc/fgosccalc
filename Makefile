.PHONY: build
.PHONY: sync
.PHONY: docker-build docker-run docker-deploy

build:
	npm run build

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
