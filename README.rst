==========
Servicemon
==========

|Powered by Astropy| |PyPI Status| |Travis Status| |Coverage Status|

Servicemon is a tool for collecting performance information for web queries by 
repeatedly timing the queries over varying input parameters.  The features are 
available via command line and Python API.

See the `online documentation <https://servicemon.readthedocs.io/en/latest/>`_ 
for details on installation, customization and use.

Contributing
------------

We encourage and welcome contributions in many forms.  Please help us make this 
a positive and inclusive environment by abiding with the
`Astropy Community Code of Conduct <https://www.astropy.org/code_of_conduct.html>`_.

Bug reports and feature requests can be submitted by 
`creating a new Github issue <https://github.com/NASA-NAVO/servicemon/issues>`_.

Code and documentation changes can be submitted by 
`creating a pull request <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests>`_
from GitHub users' "forks" (i.e., copies) of the `servicemon repository <https://github.com/NASA-NAVO/servicemon>`_. 
This project follows the basic approach of Astropy's 
`development workflow <https://docs.astropy.org/en/latest/development/workflow/development_workflow.html>`_ and 
`coding guidelines <https://docs.astropy.org/en/latest/development/codeguide.html>`_.  Since servicemon was initially built using
the Astropy Package Template, 
it shares Astropy's basic development and build tools.  If you have any
questions, please file an issue (or draft pull request) to start the conversation and we'll be happy to help.

If you locally cloned this repo before March 12, 2021
"""""""""""""""""""""""""""""""""""""""""""""""""""""

The primary branch for this repo has been transitioned from ``master`` to ``main``.  If you have a local clone of this repository and want to keep your local branch in sync with this repo, you'll need to do the following in your local clone from your terminal::

   git fetch --all --prune
   # you can stop here if you don't use your local "master"/"main" branch
   git branch -m master main
   git branch -u origin/main main

If you are using a GUI to manage your repos you'll have to find the equivalent commands as it's different for different programs. Alternatively, you can just delete your local clone and re-clone!


License
-------

This project is Copyright (c) Tom Donaldson and licensed under
the terms of the BSD 3-Clause license. This package is based upon
the `Astropy package template <https://github.com/astropy/package-template>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

.. |Powered by Astropy| image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge
    
.. |Travis Status| image:: https://img.shields.io/travis/NASA-NAVO/servicemon/main?logo=travis%20ci&logoColor=white&label=Travis%20CI
    :target: https://travis-ci.org/NASA-NAVO/servicemon
    :alt: Servicemon's Travis CI Status

.. |Coverage Status| image:: https://codecov.io/gh/NASA-NAVO/servicemon/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/NASA-NAVO/servicemon
    :alt: Servicemon's Coverage Status

.. |PyPI Status| image:: https://img.shields.io/pypi/v/servicemon.svg
    :target: https://pypi.python.org/pypi/servicemon
    :alt: Servicemon's PyPI Status
