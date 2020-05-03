test: export TEST_HOSTNAME=my-hostname.bitrix24.com
test: export TEST_CLIENT_ID=my.client.id
test: export TEST_CLIENT_SECRET=MyClientSecret
test: export TEST_USER_ID=1
test: export TEST_WEBHOOK_CODE=MyWebhookCode
test: export TEST_USER_LOGIN=my.name@mail.com
test: export TEST_USER_PASSWORD=MyPassword
test:
	tox

doc:
	.\docs\make.bat html

publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*

i:
	pip install -r requirements.txt
