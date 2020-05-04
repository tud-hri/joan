# Coding standard

---
## General

We follow the coding standard as outlined in [PEP8][pep8link], with one exception the maximum column length for code is increased to 160 since we all use 19:6 screens. 
To make your life a bit easier, use linters. We recommend `flake8` or `pylint`, or the build-in functionality of pycharm

Use in editors:

*  You can install these linters in Visual Studio Code, see their instructions [here][vscodelinterlink]
*  PyCharm checks the code according to PEP8 automatically. To change the maximum line length to 160 follow these steps:

    1. Click: file -> settings
    2. In the navigation bar on the left go to: editor -> code style -> python  
    3. Open the line and wrapping tab 
    4. Change the first option (hard wrap) from 120 (default) to 160 and click oke

!!! Note
    To auto format your code in PyCharm use ctrl + alt + L

[pep8link]: https://www.python.org/dev/peps/pep-0008/
[vscodelinterlink]: https://code.visualstudio.com/docs/python/linting
[pycharmlinterlink]: https://www.google.com

---
## Python

  * Comments should not exceed 80 columns, code should not exceed 160 columns.
  * All code must be compatible with Python 3.7.
  * Use snake_case for methods, variables, attributes
  * Use CamelCase for classes
  * Functions or variables that are only for use within a class (private members) should start with an underscore (e.g. self._my_variable)
  * Use _informative_ variable names, not `self.bla = 1` or `self.whatever`. 
  * Remove any commented code once you are done with coding. 
  * [Pylint][pylintlink] or [flake8][flake8link] should not give any error or warning (few exceptions apply with external classes like `numpy` and `pygame`, etcetera).
    * To enable PyLint in Visual Studio Code, make sure you installed the Python extension. Then, use `Ctrl+Shift+P` and type `Python: Enable linting`, set it to `yes`.
    * You can also enable flake8 in Visual Studio Code in the same way. You can install flake8 through `pip install flake8`.
  * Python code follows [PEP8 style guide][pep8link].

[pylintlink]: https://www.pylint.org/
[flake8link]: https://flake8.pycqa.org/en/latest/
[pep8link]: https://www.python.org/dev/peps/pep-0008/