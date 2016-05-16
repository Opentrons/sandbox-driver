try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': "Python hardware drivers",
	'author': "OpenTrons",
	'url': 'http://opentrons.com',
	'version': '0.1',
	'install_requires': [
		'nose',
		'coverage',
		'autobahn'
	],
	'packages': ['driver','tests','controller','session'],
	'scripts': ['./bin/driver-test'],
	'name': 'driver'
}

setup(**config)
