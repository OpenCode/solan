# Copyright 2019 Francesco Apruzzese <cescoap@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from setuptools import setup


setup(name='solan',
      version='0.1.0',
      description='Solan',
      url='https://github.com/OpenCode/solan',
      author='Francesco Apruzzese',
      author_email='cescoap@gmail.com',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='solan share sharing lan',
      license='AGPL',
      packages=['solan'],
      install_requires=[
          'click',
      ],
      entry_points = {
        'console_scripts': ['solan=solan.core:run'],
        },
    zip_safe=False)
