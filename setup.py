"""
grafliq setup module.
"""

import io
import re

from setuptools import find_namespace_packages, setup


with io.open('README.md', 'rt', encoding='utf8') as readme_file:
    README = readme_file.read()

with io.open('src/grafliq/__init__.py', 'rt', encoding='utf8') as version_file:
    VERSION = re.search(r"__version__ = '(.*?)'", version_file.read()).group(1)

PACKAGES = [
    'requests==2.32.3',
]

TEST_PACKAGES = PACKAGES + [
    'pytest==8.3.2',
    'pytest-cov==5.0.0',
    'pygments==2.18.0',
]

setup(
    name='grafliq',
    version=VERSION,
    url='https://github.com/mononobi/grafliq',
    project_urls={
        # 'Documentation': '',
        'Code': 'https://github.com/mononobi/grafliq',
        'Issue tracker': 'https://github.com/mononobi/grafliq/issues',
    },
    license='BSD-3-Clause',
    author='mono',
    author_email='mononobi@gmail.com',
    maintainer='mono',
    maintainer_email='mononobi@gmail.com',
    description='A simple and pythonic way to query GraphQL endpoints '
                'without having to do any string manipulation.',
    long_description=README,
    long_description_content_type='text/markdown',
    keywords=('graphql python grafliq graphql-query pythonic graphql-client '
              'graphql-tool pythonic-graphql-tool graphql-for-humans pythonic-graphql '
              'graphql-query-builder graphql-queries graphql-query-generator'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_namespace_packages('src', exclude=('tests', 'tests.*')),
    package_dir={'': 'src'},
    package_data={'': ['*']},
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=PACKAGES,
    extras_require={
        'tests': TEST_PACKAGES,
    },
)
