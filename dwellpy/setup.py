"""Setup script for Dwellpy."""

from setuptools import setup, find_packages
import os

# Read version from version file
version_file = os.path.join(os.path.dirname(__file__), 'dwellpy', '__version__.py')
version_info = {}
with open(version_file, 'r', encoding='utf-8') as f:
    exec(f.read(), version_info)

# Read README for long description
readme_file = os.path.join(os.path.dirname(__file__), 'docs', 'README.md')
long_description = ""
if os.path.exists(readme_file):
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Read requirements
requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
requirements = []
if os.path.exists(requirements_file):
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name=version_info['__title__'],
    version=version_info['__version__'],
    description=version_info['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=version_info['__author__'],
    url=version_info['__url__'],
    license=version_info['__license__'],
    
    packages=find_packages(),
    include_package_data=True,
    
    python_requires='>=3.8',
    install_requires=requirements,
    
    entry_points={
        'console_scripts': [
            'dwellpy=dwellpy.main:main',
        ],
        'gui_scripts': [
            'dwellpy-gui=dwellpy.main:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Desktop Environment :: Window Managers',
        'Topic :: System :: Hardware :: Input',
        'Topic :: Adaptive Technologies',
    ],
    
    keywords='accessibility dwell clicker motor disabilities assistive technology',
    
    project_urls={
        'Bug Reports': f"{version_info['__url__']}/issues",
        'Source': version_info['__url__'],
        'Documentation': f"{version_info['__url__']}/wiki",
    },
    
    package_data={
        'dwellpy': [
            'config/*.json',
            'docs/*.md',
        ],
    },
    
    zip_safe=False,  # Required for PyQt6 applications
)
