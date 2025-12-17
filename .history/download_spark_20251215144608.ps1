# 使用清华大学镜像站下载Apache Spark
# 清华大学镜像站地址: https://mirrors.tuna.tsinghua.edu.cn/apache/

# 定义下载URL和目标文件名
$mirrorUrl = "https://mirrors.tuna.tsinghua.edu.cn/apache/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz"
$localFile = "spark-3.5.0-bin-hadoop3.tgz"

# 检查文件是否已存在
if (Test-Path $localFile) {
    Write-Host "文件已存在，检查是否完整..."
    $existingFileSize = (Get-Item $localFile).Length
    Write-Host "现有文件大小: $existingFileSize 字节"
}

Write-Host "开始从清华大学镜像站下载Spark..."
Write-Host "下载URL: $mirrorUrl"

# 使用PowerShell的Invoke-WebRequest下载文件
try {
    Invoke-WebRequest -Uri $mirrorUrl -OutFile $localFile
    Write-Host "下载完成！"
    
    # 验证下载的文件
    $downloadedFileSize = (Get-Item $localFile).Length
    Write-Host "下载文件大小: $downloadedFileSize 字节"
} catch {
    Write-Host "下载失败: $_"
    exit 1
}

Write-Host "Spark下载完成，文件保存为: $localFile"