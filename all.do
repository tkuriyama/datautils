
# echo "> Running pytest" >&2
# py.test >&2

echo "\n> PyTest coverage" >&2
pytest --cov-config=.coveragerc --cov=datautils datautils/test/ >&2


echo "\n> Running pyflakes" >&2
pyflakes datautils/ >&2

echo "\n> Running mypy" >&2
mypy datautils >&2

