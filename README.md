# juegen_fastapi fastapi项目脚手架

这是一个基于 FastAPI 构建的 Web 服务项目模板，具有清晰的目录结构、完善的功能模块和良好的可扩展性。

## ✨ 项目特点

* **清晰的目录结构**: 按照功能模块化组织代码，易于维护和扩展。
* **严格的数据验证**: 使用 Pydantic 进行请求和响应数据验证。
* **异步数据库操作**: 使用 Tortoise ORM 实现高性能的异步数据库交互。
* **完善的日志系统**: 使用 Loguru 实现详细的应用日志记录。
* **统一的异常处理**: 自定义异常和全局异常处理机制，提升健壮性。
* **JWT 认证**: 使用 JSON Web Tokens 进行安全的用户认证和授权。
* **分层架构**: 模型、视图（API路由）、服务（核心逻辑）分离。
* **数据库迁移**: 使用 Aerich 管理数据库结构变更。
* **中间件支持**: 集成日志中间件，方便扩展其他中间件。
* **配置文件管理**: 通过 `config.py` 集中管理应用配置。

## 🛠️ 主要技术栈

* **Web 框架**: FastAPI
* **ORM 框架**: Tortoise ORM
* **数据验证**: Pydantic
* **用户认证**: JWT (pyjwt)
* **日志处理**: Loguru
* **数据库迁移**: Aerich
* **编程语言**: Python 3.8+

## 📂 项目结构

```
juegenfastapi/
├── api/                  # API路由 (区分内部 internal/ 和外部 external/)
├── core/                 # 核心功能 (认证, JWT, 日志, 异常处理, 生命周期)
├── model/                # 数据库模型 (Tortoise ORM)
├── schemas/              # 数据模型 (Pydantic, 含基础响应模型)
├── middleware/           # 中间件
├── utils/                # 工具类 (如加密)
├── common/               # 公共组件 (如分页)
├── database/             # 数据库配置相关
├── migrations/           # 数据库迁移文件 (Aerich)
├── static/               # 静态文件
├── logs/                 # 日志文件
├── main.py              # 应用入口
├── config.py            # 应用配置
├── TORTOISE_ORM.py      # Tortoise ORM 配置文件
├── requirements.txt     # Python 依赖
├── pyproject.toml       # 项目元数据 (含 Aerich 配置)
└── venv/                # 虚拟环境 (建议)
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <你的项目仓库地址>
cd <项目目录>
```

### 2. 创建和激活虚拟环境 (推荐)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境

* 根据需要修改 `config.py` 文件中的配置项，例如数据库连接信息、JWT 密钥等。
* 检查 `TORTOISE_ORM.py` 中的数据库连接配置是否正确。
* 确保 `pyproject.toml` 文件中的 `[tool.aerich]` 部分指向正确的 Tortoise ORM 配置。

### 5. 初始化数据库和执行迁移

```bash
# 初始化 Aerich (首次运行时需要)
aerich init -t TORTOISE_ORM.tortoise_config --location ./migrations/models

# 生成迁移文件
aerich migrate

# 应用迁移
aerich upgrade
```

*注意：你需要根据 `TORTOISE_ORM.py` 中定义的 `tortoise_config` 字典来调整 `-t` 参数。*

### 6. 运行应用

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

*`main:app` 指向 `main.py` 文件中的 `app` FastAPI 实例。*

现在，你可以通过浏览器或 API 测试工具访问 `http://localhost:8000` (或你配置的地址和端口) 来使用此应用了。API 文档通常位于 `/docs` 或 `/redoc`。

## 📝 使用说明

* **API 接口**: 查阅 `api/` 目录下的代码和 FastAPI 自动生成的文档 (`/docs`) 来了解可用的 API 接口。
* **配置**: 应用的核心配置在 `config.py` 中。
* **数据库模型**: 在 `model/` 目录下定义，使用 Tortoise ORM。
* **数据验证**: 在 `schemas/` 目录下定义 Pydantic 模型。
* **日志**: 日志配置在 `core/loguru.py`，日志文件默认输出到 `logs/` 目录。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。
