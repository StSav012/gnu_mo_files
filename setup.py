# coding: utf-8
from typing import TextIO

import setuptools

readme_f_in: TextIO
source_f_in: TextIO
with open('README.md', 'rt', encoding='utf-8') as readme_f_in, \
        open('src/gnu_mo_files/__init__.py', 'rt') as source_f_in:
    exec(next(filter(lambda s: s.strip().startswith('__version__ = '), source_f_in.readlines())))
    setuptools.setup(
        name='gnu_mo_files',
        version=locals()['__version__'],
        author='StSav012',
        author_email='stsav012@gmail.com',
        description='Read and write GNU MO files',
        long_description=readme_f_in.read(),
        long_description_content_type='text/markdown',
        url='https://github.com/stsav012/gnu_mo_files',
        project_urls={
            'Bug Tracker': 'https://github.com/stsav012/gnu_mo_files/issues',
        },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.6',
            'Typing :: Typed',
            'License :: OSI Approved :: The Unlicense (Unlicense)',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Localization',
        ],
        package_dir={'': 'src'},
        packages=setuptools.find_packages(where='src'),
        python_requires='>=3.6',
    )
