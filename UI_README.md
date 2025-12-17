# 文件监控系统 - NiceGUI界面

这是一个基于NiceGUI的图形用户界面，用于管理和监控文件变化。

## 功能特性

1. **文件监控状态管理**
   - 启动/停止文件监控
   - 实时显示监控状态

2. **文件变化记录**
   - 实时显示文件创建、修改、删除事件
   - 时间戳和文件类型信息

3. **报告生成**
   - 一键生成文件变化报告
   - 全量扫描功能

4. **Git集成**
   - 查看Git状态
   - 与Git版本控制系统集成

## 启动界面

```bash
python ui_app.py
```

然后在浏览器中访问: http://localhost:8080

## 代码质量检查

本项目提供了自定义脚本来确保代码质量，在提交代码前建议运行这些检查。

### 安装依赖

首先安装项目依赖：
```bash
pip install -r requirements.txt
```

### 自动格式化代码

运行以下命令自动格式化代码和排序导入：
```bash
# Windows
python format_code.py
# 或双击 format_code.bat

# Linux/Mac
python3 format_code.py
```

### 检查代码质量

运行以下命令检查代码质量：
```bash
# Windows
python run_checks.py
# 或双击 check_code.bat

# Linux/Mac
python3 run_checks.py
```

该脚本会检查：
- 代码格式化问题（Black）
- 导入排序问题（isort）
- 代码风格问题（Flake8）
- 重要文件完整性

### 手动运行各工具

你也可以手动运行各个工具：

```bash
# 格式化代码
black .

# 排序导入
isort .

# 检查代码风格
flake8 .
```

## 使用说明

1. **开始监控**: 点击"开始监控"按钮启动文件监控
2. **停止监控**: 点击"停止监控"按钮停止文件监控
3. **生成报告**: 点击"生成报告"按钮执行全量扫描并生成报告
4. **查看Git状态**: 点击"查看Git状态"按钮检查Git仓库状态

## 技术架构

- **前端框架**: NiceGUI (基于Python的现代UI框架)
- **后端逻辑**: 基于watchdog库的文件监控系统
- **版本控制**: Git集成
- **报告生成**: 自动生成Markdown格式的差异报告

## 注意事项

1. 确保所有依赖包已安装:
   ```bash
   pip install nicegui watchdog
   ```

2. 界面会自动连接到当前目录的Git仓库

3. 文件变化记录会实时更新显示在表格中

4. 报告会保存在`daily_reports/`目录中