from setuptools import setup
setup(
    name="datautils",
    version="0.0.1",
    packages=['datautils', 'datautils.core', 'datautils.ingest'],
    scripts=[],

    tests_require=['pytest'],
    install_requires=[],
    package_data={},

    author='Taro Kuriyama',
    author_email='taro@tarokuriyama.com',
    description="Data Utilities in Python",
    license='MIT'
)
