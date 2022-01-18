
echo "\n> Auto formatting with autopep8..." >&2
autopep8 --in-place --aggressive --aggressive -r datautils >&2
autopep8 --in-place --aggressive --aggressive -r tests >&2

# test with MySQL server
echo "\n> PyTest coverage (assumes MySQL server)" >&2
mysql.server start  >&2
pytest --cov-config=.coveragerc --cov=datautils tests/ >&2
mysql.server stop  >&2


echo "\n> Running pyflakes" >&2
pyflakes datautils/ >&2

echo "\n> Running mypy" >&2
mypy datautils >&2

