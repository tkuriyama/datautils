"""
Fixtures.
"""
from distutils import dir_util #type: ignore
from pytest import fixture # type: ignore
import os # type: ignore

################################################################################

@fixture
def datadir(tmpdir, request):
    """From https://stackoverflow.com/a/29631801/2649084"""
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir
