install:
	python -m pip install -r requirements.txt

test:
	python -m tox

publish:
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
