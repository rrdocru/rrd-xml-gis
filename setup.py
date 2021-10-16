# coding: utf-8
import os
from setuptools import find_packages, setup
from rrd_xml_gis import name as package_name, version as package_version

with open('README.md', 'r', encoding='utf-8') as fn:
    long_description = fn.read()


def read_requirements():
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r', encoding='utf-8') as f:
        requirements = [line.rstrip() for line in f]
    return requirements


setup(
    name=package_name,
    version=package_version,
    description='Утилита преобразования xml-документа в различные ГИС-форматы',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/itthematic/rrd-xml-gis',
    author='IT-Thematic',
    author_email='inbox@it-thematic.ru',
    classifiers=[
        'Development Status :: 5 - Production/Stable'
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=read_requirements(),
    python_requires='~=3.6',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'rrd-xml-gis=rrd_xml_gis.__main__:main'
        ]
    }
)
