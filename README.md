# Git Excel Extension

| Windows | macOS |
| :---- | :------ |
| ![Windows build status][1] | _not yet available_ |

[1]: https://ci.appveyor.com/api/projects/status/gr093ijhqwtmp5s9/branch/master?svg=true


Git xltrail is an open-source Git command line extension for managing Excel workbook files in Git.

The extension makes `git diff` and `git merge` work for Excel workbooks (xls, xlt, xla, xlam, xlsx, xlsm, xlsb, xltx, xltm file formats). Git xltrail does not require Excel as it works directly on the workbook file.

With Git xltrail installed, Git can compare and merge Excel workbook files just like any other source code file.

It is written in Python, with pre-compiled binaries available for Windows.

Installation instructions and docs are available at [https://www.xltrail.com/git-xltrail](https://www.xltrail.com/git-xltrail).


## Getting Started 

### Installation
You can install the Git xltrail client on Windows, using the pre-complied binary installer.

This repository can also be built-from-source using Python and PyInstaller.


Git xltrail requires a global installation once per-machine. This can be done by
running:

```
C:\Developer>git xltrail install
```

Alternatively, initialise Git xltrail locally (per repository), using the --local option, inside the root folder of your repository’s local working copy:

```
C:\Developer>git xltrail install --local
```

### Usage

#### Diff workbooks

Get meaningful `git diff` output when comparing Excel workbook files containing VBA code.

```
C:\Developer>git diff dev..master
diff --xltrail a/Book1.xlsb b/Book1.xlsb
--- a/Book1.xlsb/VBA/Module/Module1
+++ b/Book1.xlsb/VBA/Module/Module1
@@ -1,4 +1,4 @@
 Option Explicit
 Public Function Version() As String
-   Version = "v1.0"
+   Version = "v1.1"
End Sub
```


#### Merge branches

```
C:\Developer>git merge dev
--- a/Book1.xlsb/VBA/Module/Module1
+++ b/Book1.xlsb/VBA/Module/Module1
Auto-merging Book1.xlsb
Merge made by the 'recursive' strategy.
 Book1.xlsb | Bin 8021 -> 7910 bytes
 1 file changed, 0 insertions(+), 0 deletions(-)
```



### Ignore temporary Excel files

Automatically ignore temporary `~$` Excel files (e.g. when opening `Book1.xlsb`, Excel creates a temporary file called `~$Book1.xlsb`)


## Docs

Docs are available at [https://www.xltrail.com/git-xltrail](https://www.xltrail.com/git-xltrail).


## Contributing

Please [open a new issue](https://github.com/ZoomerAnalytics/git-xltrail/issues) to report bugs or [create a pull request](https://github.com/ZoomerAnalytics/git-xltrail/pulls) to send patches.