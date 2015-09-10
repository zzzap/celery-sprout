from distutils.core import setup
from setuptools import find_packages

VERSION = '0.0.3'

setup(
    name='celery-sprout',
    packages=find_packages(),
    version=VERSION,
    description='Generate Web UI to run Celery tasks',
    author='Vladimir Makushkin',
    author_email='makushkin.v@gmail.com',
    url='https://github.com/zzzap/celery-sprout',
    license='MIT',
    download_url='https://github.com/zzzap/celery-sprout/tarball/%s' % VERSION,
    keywords=['celery'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['celery>=3.0'],
)
