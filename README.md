# Git XL - A Git Extension for Excel

(Note: Git XL was previously called "git-xltrail")

| Windows | macOS |
| :---- | :------ |
| ![Windows build status][1] | _not yet available_ |

[1]: https://ci.appveyor.com/api/projects/status/gr093ijhqwtmp5s9/branch/master?svg=true


Git XL is an open-source Git command line extension for managing Excel workbook files in Git.

The extension makes `git diff` and `git merge` work for Excel VBA (xls, xlt, xla, xlam, xlsx, xlsm, xlsb, xltx, xltm). Git XL does not require Excel as it works directly on the workbook file.

With Git XL installed, Git can diff and merge Excel VBA just like any other source code file.

It is written in Python, with pre-compiled binaries available for Windows.

Installation instructions and docs are available at [https://www.xltrail.com/git-xl](https://www.xltrail.com/git-xl).


## Getting Started 

### Installation
You can install the Git XL client on Windows, using the pre-compiled binary installer.

This repository can also be built-from-source using Python and PyInstaller.

Git XL requires a global installation once per-machine. This can be done by
running:

```
C:\Developer>git xl install
```

Alternatively, initialise Git XL locally (per repository), using the --local option, inside the root folder of your repository’s local working copy:

```
C:\Developer>git xl install --local
```

### Usage

#### Diff workbooks

Get meaningful `git diff` output when comparing Excel workbook files containing VBA code.

```
C:\Developer>git diff dev..master
diff --xl a/Book1.xlsb b/Book1.xlsb
--- a/Book1.xlsb/VBA/Module/Module1
+++ b/Book1.xlsb/VBA/Module/Module1
@@ -1,4 +1,4 @@
 Option Explicit
 Public Function Version() As String
-   Version = "v1.0"
+   Version = "v1.1"
 End Function
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


#### List workbooks

List all workbooks in your repository and get meta data on workbook content.

```
C:\Developer>git xl ls-files
./Book1.xlsb
    VBA/Document/ThisWorkbook
    VBA/Document/Sheet1
    VBA/Module/Module1
    VBA/Module/Module2
    VBA/Module/Module3
```


List all workbooks and content in your repository.

```
C:\Developer>git xl ls-files -v
./Book1.xlsb
    VBA/Document/ThisWorkbook
        Option Explicit

    VBA/Document/Sheet1
        Option Explicit

    VBA/Module/Module1
        Option Explicit
        Public Function Version() As String
            Version = "v1.0"
        End Function

    VBA/Module/Module2
        Option Explicit
        Public Function GetVersion() As String
            GetVersion = "v0.0.1"
        End Function
        Public Sub test()
            Debug.Print "hello"
            'asdasdsad
        End Sub
    VBA/Module/Module3
        Option Explicit

        Public Function GetVersion() As String
            GetVersion = "v0.0.1"
        End Function
```

## Docs

Docs are available at [https://www.xltrail.com/git-xl](https://www.xltrail.com/git-xl).


## Contributing

Please [open a new issue](https://github.com/xlwings/git-xl/issues) to report bugs or [create a pull request](https://github.com/xlwings/git-xl/pulls) to send patches.
