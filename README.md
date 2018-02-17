# Git Excel Extension

| Windows | macOS |
| :---- | :------ |
[  [Windows build status][1] | not yet available |

[1]: https://ci.appveyor.com/api/projects/status/gr093ijhqwtmp5s9/branch/master?svg=true


Git xltrail is an open-source Git command line extension for managing Excel workbook files in Git. It is written in Python, with pre-compiled binaries available for Windows.

For further info, see [https://www.xltrail.com/git-xltrail](https://www.xltrail.com/git-xltrail).


## Installing Git xltrail

You can install Git xltrail by downloading the [Binary package][https://github.com/ZoomerAnalytics/git-xltrail/releases/download/0.1.0/git-xltrail-windows-0.1.0.exe] for Windows.

Once downloaded and installed, you need to set Git xltrail up via a command line command. This only
needs to be done once per machine if installed globally or once per repository if installed with the `--local` option.

Install once globally:
```
git xltrail install
```

Install locally (per repository), using the `--local` option, inside the root folder of your repository's local working copy:

```
git xltrail install --local
```

When using the `--local` option, make sure `.gitattributes` and `.gitignore` are tracked:

```
git add .gitattributes
git add .gitignore
```


## Features

### Diff Excel VBA

Get meaningful `git diff` output when comparing Excel workbook files containing VBA code.

Without Git xltrail:
```
C:\Users\Bjoern\Developer\workbooks>git diff Book1.xlsb
diff --git a/Book1.xlsb b/Book1.xlsb
index 293e924..8438ae5 100644
Binary files a/Book1.xlsb and b/Book1.xlsb differ
```

With Git xltrail:
```
C:\Users\Bjoern\Developer\workbooks>git diff Book1.xlsb
diff --xltrail a/Book1.xlsb b/Book1.xlsb
index 293e924..8438ae5 100644
--- b/Book1.xlsb/VBA/Module1
+++ /dev/null
-Option Explicit
-
-Function Version()
-    Version = "0.1.0"
-End Sub
```


### Ignore temporary Excel files

Automatically ignore temporary `~$` Excel files (e.g. when opening `Book1.xlsb`, Excel creates a temporary file called `~$Book1.xlsb`)


## Need help?

You can get help on specific commands directly:

```
git xltrail help <subcommand>
```


## Contributing

Please [open a new issue](https://github.com/ZoomerAnalytics/git-xltrail/issues) to report bugs or [create a pull request](https://github.com/ZoomerAnalytics/git-xltrail/pulls) to send patches.