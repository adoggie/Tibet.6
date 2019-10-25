
# python setup.py bdist_egg

from setuptools import setup,find_packages

setup(
    name='camel_lib',
    version='0.2.0',
    packages = find_packages(),
    # zip_safe = False,
    description='camel libs',
    # long_description='tiny communication engine',
    author='zhangbin',
    author_email='socketref@hotmail.com',
    # keywords=('tce','rpc'),
    # platforms='Independant',
    url='',
    install_requires = ['gevent','flask'],
    scripts =[]

)
