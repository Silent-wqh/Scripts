<#
此脚本用于监视在config文件中指定的目录，并将每个目录下的一级文件和文件夹的名称写入到output文件中。

Config文件格式:
每一行应包含一个要监视的目录的完整路径。例如：
C:\Users\Username\Documents
D:\Projects
E:\Downloads
请确保每个目录的路径都正确，且脚本有足够的权限来访问这些目录。

Output文件格式:
每一行将包含一个文件或文件夹的名称，或者一个表示无法访问某个目录的错误消息。例如：
File1.txt
Folder1
无法访问目录: C:\Windows\System32
File2.docx
#>

while($true) {
    # 读取配置文件中的目录路径
    $directories = Get-Content -Path .\config\path_watcher_config.txt

    # 创建或清空输出文件
    if (Test-Path .\output\path_watcher_output.txt) {
        Clear-Content -Path .\output\path_watcher_output.txt
    } else {
        New-Item -Path .\output\path_watcher_output.txt -ItemType File
    }

    # 定义一个函数，用于列出目录下的一级文件和文件夹的名称
    function ListItems {
        param($directory)
        # 创建一个空的ArrayList来存储目录内容
        $items = New-Object System.Collections.ArrayList
        try {
            # 获取一级文件夹和文件的名称，并添加到ArrayList中
            Get-ChildItem -Path $directory |
                Select-Object -ExpandProperty Name |
                ForEach-Object { $items.Add($_) | Out-Null }
        } catch {
            # 如果无法访问目录，添加错误消息到ArrayList中
            $items.Add("无法访问目录: $directory") | Out-Null
        }
        return $items
    }

    # 遍历每个目录
    foreach ($directory in $directories) {
        # 检查目录是否存在
        if (Test-Path $directory) {
            # 列出目录下的一级文件和文件夹的名称
            ListItems $directory | ForEach-Object { Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value $_ }

        } else {
            # 如果目录不存在，输出错误消息
            Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value "目录不存在: $directory"
        }
    }
    # 每隔1小时运行一次
    Start-Sleep -Seconds 3600
}
