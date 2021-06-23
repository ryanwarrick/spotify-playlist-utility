# Note about directory:
Working Directory to execute the commands listed below is: {prjroot}/docs/

# Quickstart Cmd Used
sphinx-quickstart --extensions=myst_parser, 'autodoc'

Note: Should only be used once, to initialize the cwd as the root directory for sphinx docs.

# Instructions to rebuild package specific docs
sphinx-apidoc -o .\source ..\src\

Note: This regenerates the autodoc/apidoc documentation of Python packages listed in {prjroot}/src/

# Instructions to (re)build the docs themselves (to be ran after the above command too)
./make html

Note: Can also use the 'sphinx-build' command too, however this is easier.

# Where to view your resulting sphinx-generated doc site
{prjroot}/docs/build/html/