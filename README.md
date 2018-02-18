# Git Excel Extension

| Windows | macOS |
| :---- | :------ |
| ![Windows build status][1] | _not yet available_ |

[1]: https://ci.appveyor.com/api/projects/status/gr093ijhqwtmp5s9/branch/master?svg=true


Git xltrail is an open-source Git command line extension for managing Excel workbook files in Git. It is written in Python, with pre-compiled binaries available for Windows.

Installation instructions and docs are available at [https://www.xltrail.com/git-xltrail](https://www.xltrail.com/git-xltrail).


## Features

### Diff Excel VBA

Get meaningful `git diff` output when comparing Excel workbook files containing VBA code.

Without Git xltrail:
```
C:\Users\Bjoern\Developer\Workbooks>git diff Book1.xlsb
diff --git a/Book1.xlsb b/Book1.xlsb
index 293e924..8438ae5 100644
Binary files a/Book1.xlsb and b/Book1.xlsb differ
```

With Git xltrail:
```
C:\Users\Bjoern\Developer\Workbooks>git diff Book1.xlsb
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


## Docs

Docs are available at [https://www.xltrail.com/git-xltrail](https://www.xltrail.com/git-xltrail).


## Contributing

Please [open a new issue](https://github.com/ZoomerAnalytics/git-xltrail/issues) to report bugs or [create a pull request](https://github.com/ZoomerAnalytics/git-xltrail/pulls) to send patches.