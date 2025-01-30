dev:
	uvicorn main:app --reload --port 8001

local:
	docker build -t stock-app-proxy .
	docker run --name stock-app-proxy -p 8001:8001 --rm stock-app-proxy
	docker rmi stock-app-proxy
