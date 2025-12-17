# 文件监控服务使用说明

## 启动服务

### 方法一：直接运行 Python 脚本
```bash
python file_monitor.py
```

### 方法二：使用启动脚本（Windows）
双击运行 `start_service.bat` 文件

## Web 服务接口

服务启动后，默认监听 8080 端口，提供以下 HTTP 接口：

### 1. 查询服务状态
```
GET http://localhost:8080/status
```

响应示例：
```json
{
  "status": "running",
  "monitor_dir": "C:\\Users\\P30015874206\\Desktop\\watchdog",
  "timestamp": "2025-12-15 15:30:45"
}
```

### 2. 手动触发全量扫描
```
GET http://localhost:8080/scan
```

响应示例：
```json
{
  "status": "success",
  "message": "扫描完成",
  "report": {
    "summary": "在2025-12-15 15:30:45执行了全量扫描",
    "file_count": 12,
    "details": "共检测到 12 个文件"
  },
  "timestamp": "2025-12-15 15:30:45"
}
```

### 3. 错误处理
访问不存在的接口会返回 404 错误：
```json
{
  "status": "error",
  "message": "接口不存在",
  "available_endpoints": ["/status", "/scan"]
}
```

## 命令行使用

### 手动扫描模式
```bash
python file_monitor.py --manual-scan
```
此模式下会执行一次全量扫描并生成日报，然后立即退出。

## 配置说明

所有配置都在 `file_monitor.py` 文件中：

- `MONITOR_DIR`: 要监控的目录（默认为当前目录）
- `AI_API_URL`: AI接口的URL地址（需要替换为实际地址）
- `REPORT_SAVE_PATH`: 日报保存路径
- `WEB_PORT`: Web服务监听端口（默认为8080）

## 输出文件

- `file_changes.log`: 记录所有文件变化的日志文件
- `daily_reports/`: 存放生成的日报文件和文件差异报告的目录
- `.file_cache/`: 文件缓存目录（仅在未使用Git时创建）

## 版本控制

系统支持两种文件版本管理方式：

### Git 管理（推荐）

如果系统中安装了 Git 并且工作目录是 Git 仓库，系统将自动使用 Git 来管理文件版本。
这提供了更好的版本控制功能，包括完整的文件历史记录和差异比较。

要使用 Git 管理，请确保：
1. 系统已安装 Git
2. 工作目录已初始化为 Git 仓库（运行 `git init`）
3. Git 用户名和邮箱已配置

### 文件缓存

如果没有 Git 支持，系统将使用文件缓存机制来保存文件的历史版本。
缓存文件存储在 `.file_cache/` 目录中，结构与原始目录保持一致。

## 注意事项

1. 服务运行期间会持续监控文件变化，请不要随意终止进程
2. 如需停止服务，请按 Ctrl+C 或关闭终端窗口
3. 日报文件会按日期分组存储在 `daily_reports/` 目录中
4. Web 服务接口目前只支持 GET 请求
5. 文件差异报告会以 Markdown 格式保存，文件名为"文件+日期+变更摘要的英文"