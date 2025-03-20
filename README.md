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

### 1. 环境配置

本项目提供了`.env.example`模板文件，您可以基于此文件创建自己的`.env`文件：

```bash
# 复制模板文件创建自己的环境配置
cp .env.example .env
# 然后编辑.env文件，填入您的实际配置
```

请根据模板文件中的说明填写相应的API凭证和配置项，确保填写正确，否则程序将无法正常工作。

#### DNS管理器多域名配置

DNS管理器支持同时管理多个域名。在`.env`文件中，使用`CLOUDFLARE_ZONES`配置多个域名：

```json
CLOUDFLARE_ZONES={"example.com": "区域ID1", "example.org": "区域ID2"}
```

配置格式说明：
- 使用JSON对象格式
- 键为域名
- 值为对应的Cloudflare区域ID
- 可以配置任意数量的域名


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

确保在环境变量中设置每个存储桶的`custom_domain`和`public_domain`以便应用程序能够正确生成文件URL。

## 文件说明

- `cloudflare_dns_manager.py` - Cloudflare DNS管理工具，用于管理多个域名的DNS记录
- `cloudflare_r2_manager.py` - Cloudflare R2存储管理工具，用于文件上传和管理
- `.env.example` - 环境变量配置模板文件，包含所有需要的配置项
- `requirements.txt` - 项目依赖列表

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