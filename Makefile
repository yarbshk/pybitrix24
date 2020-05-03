test: export TEST_ACCESS_TOKEN = your_access_tokem
test: export TEST_CLIENT_ENDPOINT = https://your-domain.bitrix24.com/rest/
test: export TEST_CLIENT_ID = your.client.id
test: export TEST_CLIENT_SECRET = your_client_secret
test: export TEST_CODE = requested_authentication_code
test: export TEST_DOMAIN = your-domain.bitrix24.com
test: export TEST_REFRESH_TOKEN = requested_refresh_token
test:
	python -m unittest tests

doc:
	.\docs\make.bat html

publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*

i:
	pip install -r requirements.txt
