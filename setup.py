from setuptools import setup
from qqp import __version__

setup(
    name='qqp',
    version=__version__,
    description='Scraper y API de la base de datos QQP de PROFECO',
    url='https://github.com/opintel/opi-infraestructura/',
    author='Francisco Vaquero',
    author_email='f.vquero@opianalytics.com',
    keywords='d3, opi, cli',
    install_requires=['requests==2.18.4', 'luigi==2.7.5', 'SQLAlchemy==1.2.8', 'falcon==1.4.1'],
    include_package_data=True
)
