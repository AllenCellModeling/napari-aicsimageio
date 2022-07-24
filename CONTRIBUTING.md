# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

## Get Started!

Ready to contribute? Here's how to set up `napari-aicsimageio` for local development.

1. Fork the `napari-aicsimageio` repo on GitHub.

2. Clone your fork locally:

    ```bash
    git clone git@github.com:{your_name_here}/napari-aicsimageio.git
    ```

3. Install the project in editable mode. (It is also recommended to work in a virtualenv or anaconda environment):

    ```bash
    cd napari-aicsimageio/
    pip install -e .[dev]
    ```

    If you are working on a Linux based machine you may need to additionally install
    some QT setup libraries

    ```bash
    sudo apt-get install -y libdbus-1-3 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xinput0 libxcb-xfixes0 xvfb
    ```

4. Create a branch for local development:

    ```bash
    git checkout -b {your_development_type}/short-description
    ```

    Ex: feature/read-tiff-files or bugfix/handle-file-not-found<br>
    Now you can make your changes locally.

5. Download test resources:

    ```bash
    python scripts/download_test_resources.py
    ```

6. When you're done making changes, check that your changes pass linting and
   tests, including testing other Python versions with make:

    ```bash
    make build
    ```

7. Commit your changes and push your branch to GitHub:

    ```bash
    git add .
    git commit -m "Resolves gh-###. Your detailed description of your changes."
    git push origin {your_development_type}/short-description
    ```

8. Submit a pull request through the GitHub website.

## Deploying

A reminder for the maintainers on how to deploy.
Make sure the main branch is checked out and all desired changes
are merged. Then run:

```bash
$ git tag -a "vX.Y.Z" -m "vX.Y.Z"
$ git push upstream --follow-tags
```

(The `-a` flag indicates an [annotated tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging))

This will trigger the `publish` step in the main github workflow, which will build the package
and upload it to PyPI.
