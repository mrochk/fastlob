.PHONY: test typecheck lines clean

run:
	@python3 main.py

test: 
	@python -m unittest discover test

benchmark:
	@python3 benchmark.py

typecheck: 
	@mypy pylob

lines:
	@find pylob -name "*.py" | xargs wc -l

clean:
	@rm -rf .hypothesis .mypy_cache __pycache__ pylob.egg-info