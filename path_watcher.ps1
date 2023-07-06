<#
使用说明：

这个PowerShell脚本用于监视用户在配置文件中指定的一个或多个目录，列出这些目录下的一级文件和文件夹的名称，并将这些名称写入用户指定的输出文件中。脚本会定期检查这些目录，如果有任何变化，脚本会更新输出文件。

配置文件格式：

配置文件应该是一个JSON文件，包含以下两个字段：

- `currentLocation`：一个字符串，表示脚本运行的当前目录。
- `watchedDirectories`：一个字符串数组，表示要监视的目录的路径。

以下是一个配置文件的示例：

```json
{
  "currentLocation": "C:\\Users\\name",
  "watchedDirectories": [
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\Users\\name2\\AppData\\Local"
  ]
}
```

输出文件格式：

输出文件是一个文本文件，其中包含用户在配置文件中指定的一个或多个目录下的一级文件和文件夹的名称，每个名称占一行。名称按照在文件系统中的出现顺序列出，不进行排序。如果一个目录不存在或无法访问，程序会输出一个错误消息，并继续处理其他目录。

运行脚本：

你可以使用以下命令来运行这个脚本：

```powershell
.\path_watcher.ps1 -configPath config_path -interval interval
```

其中，`config_path`是配置文件的路径，`interval`是脚本检查目录变化的间隔时间，单位是秒。如果你不提供这两个参数，脚本将使用默认的配置文件路径（脚本所在的目录下的"config\path_watcher_config.json"文件）和默认的间隔时间（3600秒）。
#>


# 定义一个命令行参数
param(
    [string]$configPath = "$PSScriptRoot\config\path_watcher_config.json",
    [int]$interval = 3600
)

while ($true) {
    # 读取配置文件
    $config = Get-Content -Path $configPath | ConvertFrom-Json

    # 切换到currentLocation指定的目录
    Set-Location -Path $config.currentLocation

    # 获取要监视的目录路径
    $directories = $config.watchedDirectories

    # 创建或清空输出文件
    if (Test-Path .\output\path_watcher_output.txt) {
        Clear-Content -Path .\output\path_watcher_output.txt
    }
    else {
        New-Item -Path .\output\path_watcher_output.txt -ItemType File
    }

    # 定义一个函数，用于列出目录下的一级文件和文件夹的名称
    function ListItems {
        param($directory)
        try {
            # 获取一级文件夹的名称，并写入输出文件
            Get-ChildItem -Path $directory -Directory |
            Select-Object -ExpandProperty Name |
            ForEach-Object { Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value $_ }
            # 获取一级文件的名称，并写入输出文件
            Get-ChildItem -Path $directory -File |
            Select-Object -ExpandProperty Name |
            ForEach-Object { Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value $_ }
        }
        catch {
            # 如果无法访问目录，输出错误消息
            Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value "无法访问目录: $directory"
        }
    }

    # 遍历每个目录
    foreach ($directory in $directories) {
        # 检查目录是否存在
        if (Test-Path $directory) {
            # 列出目录下的一级文件和文件夹的名称
            ListItems $directory
        }
        else {
            # 如果目录不存在，输出错误消息
            Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value "目录不存在: $directory"
        }
    }

    Start-Sleep -Seconds $interval
}