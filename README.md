# Flatpak-Python-auto-dependencies
Automatically generate the flatpak "module" json with the required dependencies for a given Python pypi package.

## Why should I use it?
If you are creating a flatpak manifest and your application requires some Python pypi packages, you also need to manually check all the dependencies of your dependencies and so on.

This script will do the work for you!

## How to
Execute the script and pass as arguments your dependencies

For example:
```
$ python3 flatpak_auto_pip.py automat
```

You can see the output of this command [here](example.output.json)

It is also supported the listing of multiple dependencies at ones:
```
$ python3 flatpak_auto_pip.py automat cffi
```

In the same folder will be created an `output.json` file containing all the required dependencies.
