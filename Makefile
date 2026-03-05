.PHONY: install run debug clean lint lint-strict
PYTHON := python3
CONFIG ?= config/config.txt

install:
	cd mlx_CLXV && make
	cd mlx_CLXV && bash pybuild.sh
	$(PYTHON) -m pip install mlx_CLXV/python/dist/mlx-2.2-py3-none-any.whl
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".mypy_cache" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
