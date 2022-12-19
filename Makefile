SHELL:=/usr/bin/env bash

.PHONY: style
style: format lint

.PHONY: format
format:
	black .
	isort .
	pycln .

.PHONY: lint
lint:
	mypy --install-types --non-interactive .
	flake8 .
	doc8 -q docs

.PHONY: unit
unit:
ifeq ($(ci),1)
	pytest --no-testmon
else
	pytest --no-cov
endif

.PHONY: package
package:
	poetry check
	pip check
	safety check --full-report

.PHONY: test
test: style package unit
