# Contributing to JOAN

We are more than happy to accept contributions!

How can I contribute?

- Reporting bugs and issues
- Feature requests
- Improving documentation
- Code contributions

---
## Reporting bugs and issues

If you find bugs or have other issues, use our [Issue tracker][issueslink]{target="_blank"}. Before creating a new issue, please check if a similar issue has already been reported. Select the 'bug' template in the issue tracker and fill out as much as you can. Only then we can properly address the bug!
Also check the [documentation][docslink]{target="_blank"}. <!--and FAQ-->

[issueslink]: https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan/issues
[docslink]: http://joan.readthedocs.io

---
## Feature requests

Check the [issue tracker list][issueslink]{target="_blank"} and filter on the label `feature` to check if a similar feature has been already requested. If so, please add information in the already existing feature if something is missing. Please submit your request as a new issue and select the 'feature request' template in the issue tracker.

[issueslink]: https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan/issues

---
## Improving documentation

Everyone can agree that good documentation is awesome to have. If you feel something is missing in the documentation, please don't hesitate to open an issue to let us know. Even better, if you think you can improve it yourself, it would be a great contribution!

We build our documentation with [MkDocs](http://www.mkdocs.org/){target="_blank"} based on the Markdown files inside the `docs` folder. You can either directly modify them on the GitLab repository or locally on your machine.

Once you are done with your changes, please submit a pull-request.

!!! tip
    You can build and serve it locally (at <http://127.0.0.1:8000>) by running `mkdocs`
    in the project's main folder.

```sh
  > sudo pip install mkdocs
  > mkdocs serve
```

---
## Code contributions

The code is never done, so if you want to help out, awesome!

Before starting hands-on on coding, please check out our [issue board][issueboard]{target="_blank"} to see if we are already working on that particular issue. In case of doubt or to discuss how to proceed, please contact one of us.

[issueboard]: https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan/issues

#### Coding standard

Please follow the current [coding standard](contributing-coding-standard.md) when submitting new code.

#### Pull-requests

Once you think your contribution is ready to be added to JOAN, please submit a pull-request.

Try to be as descriptive as possible when filling the pull-request description. Adding images and gifs may help people to understand your changes or new
features.

<!-- Please note that there are some checks that the new code is required to pass
before we can do the merge. The checks are automatically run by the continuous
integration system, you will see a green tick mark if all the checks succeeded.
If you see a red mark, please correct your code accordingly. -->

###### Checklist

<!--
  If you modify this list please keep it up-to-date with pull_request_template.md
-->

  - [ ] Your branch is up-to-date with the `master` branch and tested with latest changes
  - [ ] Extended the README / documentation, if necessary
  - [ ] The code adheres to PEP8, please use `flake8` or `pylint` to check the code for consistency (see [coding standard](contributing-coding-standard.md))
  - [ ] Code compiles correctly
