run:
	@python3 main.py

test: 
	@python3 -m unittest test/*.py

benchmark:
	@python3 benchmark.py

typecheck: 
	@mypy pylob

lines:
	@find pylob -name "*.py" | xargs wc -l
