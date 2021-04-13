SRCPATH := $(CURDIR)
PROJECTNAME := $(shell basename $(CURDIR))
FORWARDVIEW_IMAGE_NAME = forwardview:0.0.1
DOWNLOADER_IMAGE_NAME = downloader:0.0.1

requirements: .requirements.txt
env: venv/bin/activate

.requirements.txt: requirements.txt
	$(shell . venv/bin/activate && pip install -r requirements.txt)

build-app: ## Build docker image for forwardview app
	@docker image inspect $(FORWARDVIEW_IMAGE_NAME) 1>/dev/null || DOCKER_BUILDKIT=1 docker build \
		-t $(FORWARDVIEW_IMAGE_NAME) \
		-f provision/dockerfile.app \
		.
	@docker system prune -f

build-downloader: ## Build docker image for downloader app
	@docker image inspect $(DOWNLOADER_IMAGE_NAME) 1>/dev/null || DOCKER_BUILDKIT=1 docker build \
		-t $(DOWNLOADER_IMAGE_NAME) \
		-f provision/dockerfile.downloader \
		.
	@docker system prune -f

up: # run docker images locally
	docker-compose -f provision/docker-compose.yml up -d

down:
	docker-compose -f provision/docker-compose.yml stop && docker-compose -f provision/docker-compose.yml rm -f && docker system prune -f

update: env
	venv/bin/python3 -m pip install -U pip poetry
	poetry update
	poetry export -f requirements.txt --output requirements.txt --without-hashes

format: env
	$(shell . venv/bin/activate && isort ./)
	$(shell . venv/bin/activate && black ./)

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name 'poetry.lock' -delete
	find . -name 'Pipefile.lock' -delete

help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'