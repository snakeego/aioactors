VERSION = 1.0

.DEFAULT_GOAL = version
.PHONY: version
version:
	@ echo "Script version:" $(VERSION)
	@ echo '---'
	@ echo "App: `/usr/bin/env python setup.py --name`"
	@ echo "Version: `/usr/bin/env python setup.py --version`"
	@ echo "Description: `/usr/bin/env python setup.py --description`"
	@ echo '---'


.PHONY: lint
lint:
	@ flake8
	@ mypy .

.PHONY: coverage
coverage: ARGS = "-x"
coverage:
	@ rm -rf htmlcov
	@ py.test tests --cov ${ARGS}

.PHONY: test
test: ARGS = "-vx"
test: 
	@ py.test tests ${ARGS}


.PHONY: update
update: build push clean

.PHONY: build
build: 
	@ python setup.py sdist

.PHONY: push
push:
	@ twine upload --skip-existing dist/*

.PHONY: clean
clean:
	@ rm -rf dist *.egg-info