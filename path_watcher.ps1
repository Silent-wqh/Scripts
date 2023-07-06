# 读取配置文件中的目录路径
$directories = Get-Content -Path .\config\path_watcher_config.txt

# 创建或清空输出文件
if (Test-Path .\output\path_watcher_output.txt) {
    Clear-Content -Path .\output\path_watcher_output.txt
} else {
    New-Item -Path .\output\path_watcher_output.txt -ItemType File
}

# 遍历每个目录
foreach ($directory in $directories) {
    # 检查目录是否存在
    if (Test-Path $directory) {
        try {
            # 获取一级文件夹的名称，并写入输出文件
            Get-ChildItem -Path $directory -Directory |
                Select-Object -ExpandProperty Name |
                ForEach-Object { Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value $_ }
            # 获取一级文件的名称，并写入输出文件
            Get-ChildItem -Path $directory -File |
                Select-Object -ExpandProperty Name |
                ForEach-Object { Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value $_ }
        } catch {
            # 如果无法访问目录，输出错误消息
            Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value "无法访问目录: $directory"
        }
    } else {
        # 如果目录不存在，输出错误消息
        Add-Content -Encoding utf8 -Path .\output\path_watcher_output.txt -Value "目录不存在: $directory"
    }
}
