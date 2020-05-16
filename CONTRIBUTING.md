# Contributing
It's an open source project and we love to receive contributions from our community — you! There are many ways to contribute, from writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests or writing code which can be incorporated into pybitrix24 itself.

All members of our community are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md). Please make sure you are welcoming and friendly in all of our spaces.

## Issues

Before you submit an issue, please **search the issue tracker first**, maybe an issue for your problem already exists and the discussion might inform you of workarounds readily available.

We want to fix all the issues as soon as possible, but before fixing a bug we need to reproduce and confirm it. In order to reproduce bugs we ask you to **provide a minimal reproduction scenario** that include:
- Version of the client used.
- Environment information (3rd-party libraries, technology stack etc.).
- **A use-case that fails!**

## Pull requests
**Working on your first Pull Request?** You can learn how from this free series, [How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github).

If you would make PR for something that is bigger than a one or two line fix:
1. Be sure you are following:
    - The code style for the project: [PEP-8](https://www.python.org/dev/peps/pep-0008/).
    - Commit message convention: sentence case, present time.
1. Create your own fork of the code.
1. Do some changes in your fork.
1. Add automated tests covering the changes.
1. Submit a pull request.

## Running tests
1. Replace environment variables with real values in [Makefile](Makefile).
1. Run all automated tests (unit and E2E):
    ```shell script
    make test
    ```
