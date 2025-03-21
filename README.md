# Cloudflare 工具集

这是一个Python GUI工具集，用于管理Cloudflare的DNS记录和R2存储服务。

## 功能

### Cloudflare DNS 管理器
- 查看所有DNS记录
- 添加新DNS记录
- 编辑现有DNS记录
- 删除DNS记录
- 多域名支持（可在界面中快速切换不同域名）

### Cloudflare R2 存储管理器
- 多存储桶支持（可在界面中快速切换不同存储桶）
- 文件上传（支持单个文件和整个文件夹）
- 大文件分片上传
- 文件浏览和管理
- 下载文件
- 删除文件/文件夹
- 生成公共分享链接
- 自定义域名支持
- 拖放上传支持
- 导出文件URL列表

## 使用方法

### 1. 配置说明

本项目使用JSON配置文件存储凭证和设置，所有配置文件保存在脚本所在的同一目录中：

- `cloudflare_manager.json` - Cloudflare DNS管理器配置文件
- `cloudflare_r2_manager.json` - Cloudflare R2存储管理器配置文件

配置文件会在首次运行程序时自动创建，您可以在程序界面中通过"设置凭证"按钮进行配置。

### 2. 安装依赖

可以使用requirements.txt一次性安装所有依赖：

```bash
pip install -r requirements.txt
```

或者手动安装各个依赖：

```bash
pip install requests==2.32.3 PyQt6==6.8.1 boto3==1.37.17 urllib3==2.3.0 python-dotenv==1.0.1 cloudflare==4.1.0 pillow==11.1.0
```

### 3. 运行程序

Cloudflare DNS管理器:
```bash
python cloudflare_dns_manager.py
```

Cloudflare R2存储管理器:
```bash
python cloudflare_r2_manager.py
```

## 获取必要的API凭证

### Cloudflare API令牌和区域ID
1. 登录Cloudflare控制面板
2. 创建API令牌: 转到用户个人资料 > API令牌 > 创建令牌
3. 获取区域ID: 在域名概览页面的右侧信息卡片中可以找到

您可以使用两种方式进行认证:
- API Token（推荐）: 更安全的方式，可以设置有限的权限
- Global API Key + Email: 全局API密钥方式，拥有完整账户权限

### Cloudflare R2凭证
1. 登录Cloudflare控制面板
2. 进入R2存储服务
3. 创建或选择已有的存储桶
4. 在"管理R2 API令牌"中创建新的令牌
5. 记录下访问密钥ID和私有访问密钥
6. 注意账户ID，这将用于构建端点URL

## R2存储桶配置

R2存储管理器支持配置多个存储桶，每个存储桶可以设置:

- **存储桶标识**: 在程序中显示的名称
- **存储桶名称**: 实际的R2存储桶名称
- **自定义域名**: 用于通过自定义域名访问文件（如果已配置）
- **R2.dev公共域名**: 公共访问域名（格式为 `pub-xxxxxxxx.r2.dev`）

## 自定义域设置

要使用自定义域分享R2文件，需要：

1. 在Cloudflare控制面板中配置自定义域
2. 在R2存储桶设置中启用公共访问
3. 配置自定义域名的DNS记录指向R2存储桶

如果不使用自定义域，可以使用R2的公共域名访问文件，格式为：
`https://pub-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.r2.dev/<file_path>`

## 文件说明

- `cloudflare_dns_manager.py` - Cloudflare DNS管理工具，用于管理多个域名的DNS记录
- `cloudflare_r2_manager.py` - Cloudflare R2存储管理工具，用于文件上传和管理
- `cloudflare_manager.json` - Cloudflare DNS管理器配置文件（自动创建）
- `cloudflare_r2_manager.json` - Cloudflare R2存储管理器配置文件（自动创建）
- `requirements.txt` - 项目依赖列表

## 安全说明

所有凭证信息存储在程序所在目录下的配置文件中。如果在共享环境中使用本工具，请确保配置文件的安全性，避免未授权访问。

## 开发与贡献

欢迎贡献代码或提出问题！如果您想要参与本项目的开发：

1. Fork 这个仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件 