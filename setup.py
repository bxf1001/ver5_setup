from setuptools import setup, find_packages

setup(
    name='PhonePortal',
    version='5',
    packages=find_packages(),
    package_data={'': ['data/*', 'icons/*']},
    entry_points={
        'console_scripts': [
            'your-app = your_module:main_func',
        ],
    },
    install_requires=[
        'pywinauto','PyQt6','xlsxwriter','reportlab','keyboard'
        # other packages your project depends on
    ],
)