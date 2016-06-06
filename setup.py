from setuptools import find_packages, setup


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
	'packages': find_packages(),
	'scripts': [
		'bin/apollo-start'
	],
	'name': 'driver'
}

setup(**config)
