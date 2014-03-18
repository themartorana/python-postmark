import os
from distutils.core import setup

readme = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(readme).read()

setup(
    name = "python-postmark",
    version = "0.4.0",
    packages = ['postmark'],
    author = "Dave Martorana (http://davemartorana.com), Richard Cooper (http://frozenskys.com), Bill Jones (oraclebill), Dmitry Golomidov (deeGraYve)",
    license = 'BSD',
    description = "Postmark library for Python 2.6 and greater.",
    long_description = long_description,
    url = "http://github.com/themartorana/python-postmark",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
    ]
)
