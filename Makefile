.PHONY: test typecheck lines clean

run:
	@python3 main.py

test: 
	@echo "-- TESTING FOR BASE CLASSES:"
	@python3 -m unittest discover test -vvv

	@echo "-- TESTING FOR GTC ORDERS:"
	@python3 -m unittest discover test/GTC -vvv

	@echo "-- TESTING FOR FOK ORDERS:"
	@python3 -m unittest discover test/FOK -vvv

	@echo "-- TESTING FOR GTD ORDERS:"
	@python3 -m unittest discover test/GTD -vvv

benchmark:
	@python3 benchmark.py

typecheck: 
	@mypy pylob

lines:
	@find pylob -name "*.py" | xargs wc -l

clean:
	@rm -rf build .hypothesis .mypy_cache __pycache__ pylob.egg-info
