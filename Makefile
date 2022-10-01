.SHELL := /bin/bash
package := $(shell pdm show --name)
version := $(shell pdm show --version)
sdist := dist/$(package)-$(version).tar.gz
wheel := dist/$(package)-$(version)-py3-none-any.whl
sources := $(shell find src -type f -print)
venv := .venv/pyvenv.cfg

.PHONY: build
build: $(sdist) $(wheel)


$(sdist) $(wheel): $(sources) $(venv) pyproject.toml
	pdm build


.PHONY: venv
venv: $(venv)

pdm.lock: pyproject.toml
	pdm lock

$(venv): pdm.lock
	pdm sync --dev
	touch $@


.PHONY: shell
shell: $(venv)
	$(.SHELL) -l


.PHONY: lint
lint: $(venv)
	pdm run pylint src
	pdm run mypy src


clean:
	rm -rf .venv build dist


.PHONY: fmt
fmt:
	pdm run isort src
	pdm run black src
