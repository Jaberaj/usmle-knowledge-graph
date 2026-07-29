.PHONY: install lint typecheck test validate build-db build-bundles quality release all
install:
	python3 -m pip install -e '.[dev]'
lint:
	ruff check .
typecheck:
	mypy src
test:
	pytest
validate:
	python3 -m usmle_kb validate
build-db:
	python3 -m usmle_kb build sqlite && python3 -m usmle_kb build postgres
build-bundles:
	python3 -m usmle_kb build bundles
quality:
	python3 -m usmle_kb quality-report
release:
	python3 -m usmle_kb build release
all: lint typecheck test validate build-db build-bundles quality release
