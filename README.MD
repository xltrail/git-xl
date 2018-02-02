# Git Excel Extension

Git xltrail is a client command line extension and [specification](docs/spec.md) for
managing Excel files with Git. It is written in Python, with pre-compiled
binaries available for Windows. 

## Getting Started

You can install Git xltrail by downloading the [Binary package][rel] for Windows.

Once installed, you need to setup the global Git hooks for Git xltrail. This only
needs to be done once per machine.

```
$ git xltrail install
```

Alternatively, you can enable git-xltrail on specific repositories instead of always having it on for all of the repositories. Instead of running git xltrail install and enabling git-xltrail for that user, you can use this on a per repository basis:

```
$ git xltrail install --local
```
