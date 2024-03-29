
echo "\n> Auto formatting with autopep8..." >&2
autopep8 --in-place --aggressive --aggressive -r datautils >&2
autopep8 --in-place --aggressive --aggressive -r tests >&2

# ignore MySQL related tests
echo "\n> PyTest coverage" >&2
pytest --ignore-glob='**/*mysql*.py' --cov-config=.coveragerc --cov=datautils tests/ >&2


echo "\n> Running pyflakes" >&2
pyflakes datautils/ >&2

echo "\n> Running mypy" >&2
mypy datautils >&2

