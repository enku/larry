.SHELL := /bin/bash
package := $(shell pdm show --name)
version := $(shell pdm show --version)
sdist := dist/$(package)-$(version).tar.gz
wheel := dist/$(package)-$(version)-py3-none-any.whl
sources := $(shell find src -type f -print)

.PHONY: build
build: $(sdist) $(wheel)


$(sdist) $(wheel): $(sources) pyproject.toml
	pdm build


pdm.lock: pyproject.toml
	pdm lock


.PHONY: lint
lint:
	pdm run pylint src
	pdm run mypy src


clean:
	rm -rf .venv build dist __pypackages__


.PHONY: fmt
fmt:
	pdm run isort src
	pdm run black src
