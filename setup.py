from setuptools import setup, find_packages

setup(
    name='cratis-gen',
    version='1.0.4',
    packages=find_packages(),

    url='',
    license='Private',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Cratis generator.',
    long_description='',

    package_data={
        'cratis_generator': ['templates/*.tpl']
    },

    install_requires=[
        "pyparsing",
        "termcolor",
        "autopep8",
        "django<1.11",
        'pip>8.0.0',
        'tree-format',
        'python-dateutil',
        'wheel',
        'click',
        'jinja2',
        # 'google-pasta'
    ],

    entry_points={
        'console_scripts': [
            'django-gen = cratis_generator.cli:django_gen',
        ]
    },
)
