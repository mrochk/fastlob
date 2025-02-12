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


.PHONY: test typecheck lines