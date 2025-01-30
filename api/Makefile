cov := coverage run -m pytest
cov_port := 5500
url := http://localhost:$(cov_port)

dev:
	python3 manage.py runserver

user:
	python3 manage.py createuser neto neto

superuser:
	python3 manage.py createuser super super --is-superuser

cov:
	$(cov)
	coverage report

hcov:
	$(cov)
	coverage html
	python -c "import webbrowser; webbrowser.open_new_tab('$(url)')"
	python -m http.server -d .coverage/html-report $(cov_port)

test:
	docker build -t stock-app-api-testing --file docker/testing/Dockerfile .
	docker run --env-file docker/testing/testing.env --rm stock-app-api-testing
	docker rmi stock-app-api-testing

local:
	docker build -t stock-app-api-staging --file docker/staging/Dockerfile .
	docker run --name stock-app-api-staging -p 8000:8000 --env-file docker/staging/staging.env --rm stock-app-api-staging
	docker rmi stock-app-api-staging
