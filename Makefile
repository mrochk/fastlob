run:
	@python3 main.py

test: 
	@python3 -m unittest tests/*.py

benchmark:
	@echo 'not implemented'

typecheck: 
	@mypy pylob

lines:
	@find pylob -name "*.py" | xargs wc -l
