# Copyright 2018 ILSP/Athena R.C. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#     copyright notice, this list of conditions and the following
#     disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials
#     provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY ILSP/Athena R.C. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ILSP/Athena R.C. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of ILSP/Athena R.C.

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='elrc-share-client',
      version='1.0.0',
      description='Client with CLI for CREATE, READ, UPDATE and download operations on ELRC-SHARE repository',
      long_description=readme(),
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
      ],
      url='https://github.com/MiltosD/ELRC-Client',
      author='Miltos Deligiannis',
      author_email='mdel@ilsp.gr',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'attrs==18.2.0',
          'certifi==2018.8.24',
          'chardet==3.0.4',
          'cmd2==0.9.6',
          'colorama==0.4.0',
          'deepdiff==3.3.0',
          'idna==2.7',
          'jsonpickle==1.',
          'lxml==4.2.5',
          'pyperclip==1.7.0',
          'pyreadline==2.1',
          'requests==2.20.0',
          'urllib3==1.23',
          'wcwidth==0.1.7',
          'xmltodict==0.11.0'
      ],
      entry_points={
          'console_scripts': ['elrc-shell=elrc_client.bin.elrc_shell:main'],
      },
      zip_safe=False)
