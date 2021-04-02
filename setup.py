from setuptools import setup
setup(
    name="datautils",
    version="0.3.0",
    packages=['datautils', 'datautils.core', 'datautils.network',
              'datautils.json'],
    scripts=['datautils/bin/jbro'],

    tests_require=['pytest'],
    install_requires=[],
    package_data={},

    author='Taro Kuriyama',
    author_email='taro@tarokuriyama.com',
    description="Data Utilities in Python",
    license='MIT'
)
