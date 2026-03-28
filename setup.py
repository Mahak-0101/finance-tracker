from setuptools import setup, find_packages

setup(
    name="finance-tracker-pro",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python",
        "matplotlib"
    ],
    entry_points={
        'console_scripts': [
            'finance-tracker=finance_tracker.app:main'
        ]
    },
    author="Mahak",
    description="Premium Finance Tracker Desktop App",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
