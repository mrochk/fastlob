.PHONY: test test-base test-FOK test-GTC test-GTD typecheck lines clean

run:
	@python3 main.py

test: test-base test-GTC test-FOK test-GTD

test-base:
	@echo "-- TESTING FOR BASE CLASSES:"
	@python3 -m unittest discover test -vvv

test-GTC:
	@echo "\n-- TESTING FOR GTC ORDERS:"
	@python3 -m unittest discover test/good-till-canceled -vvv

test-FOK:
	@echo "\n-- TESTING FOR FOK ORDERS:"
	@python3 -m unittest discover test/fill-or-kill -vvv

test-GTD:
	@echo "\n-- TESTING FOR GTD ORDERS:"
	@python3 -m unittest discover test/good-till-date -vvv

typecheck: 
	@mypy fastlob

lines:
	@find fastlob -name "*.py" | xargs wc -l

clean:
	@rm -rf build .hypothesis .mypy_cache __pycache__ pylob.egg-info .vscode .ipynb_checkpoints
