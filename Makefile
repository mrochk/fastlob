run:
	@python3 main.py

test:
	@python3 -m unittest tests/*.py

lines:
	@find pylob -name "*.py" | xargs wc -l
