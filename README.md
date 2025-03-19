# Cloudflare 工具集

这是一个Python GUI工具集，用于管理Cloudflare的DNS记录和R2存储服务。

## 功能

### Cloudflare DNS 管理器
- 查看所有DNS记录
- 添加新DNS记录
- 编辑现有DNS记录
- 删除DNS记录

### Cloudflare R2 存储管理器
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

### 1. 环境配置

在项目根目录创建`.env`文件，包含以下内容：

```
# DNS管理器所需配置
CLOUDFLARE_API_TOKEN=你的Cloudflare API令牌
CLOUDFLARE_ZONE_ID=你的域名区域ID

# R2管理器所需配置
CLOUDFLARE_ACCOUNT_ID=你的Cloudflare账户ID
CLOUDFLARE_R2_ACCESS_KEY_ID=你的R2访问密钥ID
CLOUDFLARE_R2_SECRET_ACCESS_KEY=你的R2私有访问密钥
CLOUDFLARE_R2_BUCKET_NAME=你的R2存储桶名称
CLOUDFLARE_CUSTOM_DOMAIN=你的自定义域名(可选)
R2_PUBLIC_DOMAIN=你的R2公共域名(可选)
```

### 2. 安装依赖

可以使用requirements.txt一次性安装所有依赖：

```
pip install -r requirements.txt
```

或者手动安装各个依赖：

```
pip install requests python-dotenv PyQt6 boto3 urllib3
```

### 3. 运行程序

DNS管理器:
```
python cloudflare_dns_manager.py
```

R2存储管理器:
```
python cloudflare_r2_manager.py
```

## 获取必要的API凭证

### Cloudflare API令牌和区域ID
1. 登录Cloudflare控制面板
2. 创建API令牌: 转到用户个人资料 > API令牌 > 创建令牌
3. 获取区域ID: 在域名概览页面的右侧信息卡片中可以找到

### Cloudflare R2凭证
1. 登录Cloudflare控制面板
2. 进入R2存储服务
3. 创建或选择已有的存储桶
4. 在"管理R2 API令牌"中创建新的令牌
5. 记录下访问密钥ID和私有访问密钥

## 自定义域设置

要使用自定义域分享R2文件，需要：

1. 在Cloudflare控制面板中配置自定义域
2. 在R2存储桶设置中启用公共访问
3. 配置自定义域名的DNS记录指向R2存储桶

如果不使用自定义域，可以使用R2的公共域名访问文件，格式为：
`https://pub-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.r2.dev/<file_path>`

确保在环境变量中设置`R2_PUBLIC_DOMAIN`以便应用程序能够正确生成文件URL。

## 文件说明

- `cloudflare_dns_manager.py` - Cloudflare DNS管理工具，用于管理DNS记录
- `cloudflare_r2_manager.py` - Cloudflare R2存储管理工具，用于文件上传和管理 

## 截图

![image-20250319093206096](/img/cloudflare_dns_manager_main.png)

![image-20250319093307209](/img/cloudflare_r2_manager_upload.png)

## 开发与贡献

欢迎贡献代码或提出问题！如果您想要参与本项目的开发：

1. Fork 这个仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件 