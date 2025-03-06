.PHONY: test test-base test-FOK test-GTC test-GTD typecheck lines clean

run:
	@python3 main.py

test: test-base #test-GTC test-FOK test-GTD

test-base:
	@echo "-- TESTING FOR BASE CLASSES:"
	@python3 -m unittest discover test -vvv

test-GTC:
	@echo "-- TESTING FOR GTC ORDERS:"
	@python3 -m unittest discover test/GTC -vvv

test-FOK:
	@echo "-- TESTING FOR FOK ORDERS:"
	@python3 -m unittest discover test/FOK -vvv

test-GTD:
	@echo "-- TESTING FOR GTD ORDERS:"
	@python3 -m unittest discover test/GTD -vvv

typecheck: 
	@mypy fastlob

lines:
	@find fastlob -name "*.py" | xargs wc -l

clean:
	@rm -rf build .hypothesis .mypy_cache __pycache__ pylob.egg-info
