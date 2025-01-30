tests:
	docker build -t stock-app-api-testing --file api/docker/testing/Dockerfile ./api
	docker run --env-file api/docker/testing/testing.env --rm stock-app-api-testing
	docker rmi stock-app-api-testing

up:
	docker compose up

down:
	docker compose down
	docker rmi stock-app-api-service stock-app-proxy-service
