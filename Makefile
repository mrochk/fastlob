run:
	@python3 main.py

test:
	@python3 -m unittest pylob/testing/*.py

lines:
	@find pylob -name "*.py" | xargs wc -l
