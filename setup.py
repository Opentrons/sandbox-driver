try:
	from setuptools import setup, find_packages
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
	'packages': find_packages(exclude=["tests"]),
	'package_data': {
		"driver": [
			
		]
	},
	'scripts': ['./bin/driver-test'],
	'name': 'driver',
	'zip_safe': False,
	'test_suite': 'nose.collector',
}

setup(**config)
