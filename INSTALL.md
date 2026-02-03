# CoinGlass 项目依赖安装说明

## 环境要求

本项目需要以下依赖：

### Python 版本
- Python 3.8 或更高版本

### Python 包依赖
- requests>=2.25.1
- pandas>=1.3.0
- numpy>=1.21.0
- python-dotenv>=0.19.0
- apscheduler>=3.8.1
- matplotlib>=3.4.3
- seaborn>=0.11.2
- websocket-client>=1.2.1
- pytz>=2021.1
- pycryptodome>=3.10.1 (用于Crypto模块)

## 安装步骤

### 方法一：使用 pip (推荐)

1. 安装 pip（如果尚未安装）：
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip

# CentOS/RHEL/Fedora
sudo dnf install python3-pip
# 或者
sudo yum install python3-pip
```

2. 安装项目依赖：
```bash
cd /home/king/.openclaw/workspace/coinglass-alerts
pip3 install -r requirements.txt
pip3 install pycryptodome
```

### 方法二：使用虚拟环境（推荐，避免权限问题）

1. 安装 venv 和 pip：
```bash
# Ubuntu/Debian
sudo apt install python3-venv python3-pip
```

2. 创建并激活虚拟环境：
```bash
cd /home/king/.openclaw/workspace/coinglass-alerts
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
# venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install pycryptodome
```

### 方法三：使用 conda

如果你有 conda 环境：
```bash
cd /home/king/.openclaw/workspace/coinglass-alerts
conda create -n coinglass python=3.9
conda activate coinglass
pip install -r requirements.txt
pip install pycryptodome
```

## 验证安装

安装完成后，运行测试脚本验证是否安装成功：
```bash
cd /home/king/.openclaw/workspace/coinglass-alerts
python3 test_project.py
```

如果大部分测试通过（特别是模块导入和API客户端测试），说明依赖安装成功。

## WSL 环境特殊说明

如果你在 Windows Subsystem for Linux (WSL) 中运行：

1. 确保你使用的是 Ubuntu 20.04 或更高版本
2. 更新系统包：
```bash
sudo apt update && sudo apt upgrade
```

3. 安装必要的构建工具（如果需要编译某些包）：
```bash
sudo apt install build-essential libssl-dev libffi-dev python3-dev
```

## Docker 方式（可选）

如果上述方法都不适用，可以考虑使用 Docker：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pycryptodome

COPY . .

CMD ["python", "test_project.py"]
```

构建并运行：
```bash
docker build -t coinglass-alerts .
docker run coinglass-alerts
```

## 常见问题

### 1. 权限错误
如果遇到权限错误，请使用虚拟环境而不是全局安装。

### 2. 缺少系统依赖
某些包可能需要系统级别的依赖：
```bash
sudo apt install gcc g++ gfortran libopenblas-dev liblapack-dev
```

### 3. Crypto 模块问题
如果遇到 `No module named 'Crypto'` 错误：
```bash
pip uninstall pycrypto
pip install pycryptodome
```

## 故障排除

如果仍有问题，请检查：

1. Python 版本是否符合要求
2. 是否在正确的项目目录中
3. requirements.txt 文件是否完整
4. 网络连接是否正常（用于下载包）
5. 系统是否有足够的磁盘空间

## 后续步骤

一旦依赖安装成功，你就可以：

1. 运行项目测试：`python3 test_project.py`
2. 运行主程序：`python3 src/main.py`
3. 查看示例：`python3 examples/basic_usage.py`
4. 开始使用告警系统