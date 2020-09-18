# Coding standard

---
## General

We follow the coding standard as outlined in [PEP8][pep8link], with one exception the maximum column length for code is increased to 160 since we all use 19:6 screens. 
To make your life a bit easier, use linters. We recommend `flake8` or `pylint`, or the build-in functionality of pycharm

Use in editors:

*  PyCharm checks the code according to PEP8 automatically. To change the maximum line length to 160 follow these steps:

    1. Click: file -> settings
    2. In the navigation bar on the left go to: editor -> code style -> python  
    3. Open the line and wrapping tab 
    4. Change the first option (hard wrap) from 120 (default) to 160 and click oke

!!! Note
    To auto format your code in PyCharm use ctrl + alt + L

[pep8link]: https://www.python.org/dev/peps/pep-0008/
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
  * Python code follows [PEP8 style guide][pep8link].

[pylintlink]: https://www.pylint.org/
[flake8link]: https://flake8.pycqa.org/en/latest/
[pep8link]: https://www.python.org/dev/peps/pep-0008/

## Git flow

We try to use the Git flow workflow in terms of branching, feature implementation and testing and releases. For more information, visit this [link](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) and [this branching model](https://nvie.com/posts/a-successful-git-branching-model/)

### Versioning

I propose to use the [Semantic Versioning](https://semver.org/) convention for versions. Our first beta release will be v0.9.0. Each patch increases the last digit: v0.9.1. Every major version (no backwards compatibility) increases the first digit (v1.0.0); though I am not too sure about this one. Every minor version increases the second digit and resets the last: v0.10.0.

## mkdocs

We are using `mkdocs` and ReadTheDocs for our documentation. For more information on `mkdocs`, visit [this link](https://www.mkdocs.org). We have a branch for the documentation: `docs`. 

To install `mkdocs`, run:
```
pip install mkdocs
```

You can build your documentation _locally_ through:

```
mkdocs serve
```

This command builds your Markdown files into HTML and starts a development server to browse your documentation. Open up [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web browser to see your documentation. You can make changes to your Markdown files and your docs will automatically rebuild. 

Check whether your changes in the documentation work correctly before pushing them to the `docs` branch.