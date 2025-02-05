run:
	@python3 main.py

test-cheap:
	@python3 -m unittest tests/cheap/*.py

test-expensive:
	@python3 -m unittest tests/expensive/*.py

test: test-cheap test-expensive

lines:
	@find pylob -name "*.py" | xargs wc -l
