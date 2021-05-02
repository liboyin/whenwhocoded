from pathlib import Path
from setuptools import find_packages, setup

setup(
    name='whenwhocoded',
    version='0.0.1',
    description='Visualise Git repo contribution history by authors.',
    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    author='Libo Yin',
    author_email='liboyin830@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['bokeh', 'pandas', 'tqdm'],
    entry_points={
        'console_scripts': ['whenwhocoded = whenwhocoded.__main__:main'],
    },
    extras_require={
        'dev': ['mypy'],
    },
)
