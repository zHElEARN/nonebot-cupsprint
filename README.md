# nonebot-plugin-cupsprint

`nonebot-plugin-cupsprint` 是一个适用于 [NoneBot2](https://github.com/nonebot/nonebot2) 的插件，支持文件或图片的打印和扫描操作。用户可以通过简单的命令实现文件打印以及扫描图片，并可自定义扫描分辨率、模式等。

## 功能

-   **打印功能**：通过回复特定指令将文件或图片发送到打印机
-   **扫描功能**：可自定义分辨率、颜色模式、扫描区域等参数

## 安装

1. **安装插件**：

    将 `nonebot-plugin-cupsprint` 添加到您的 NoneBot2 项目中：

    ```bash
    git clone https://github.com/zHElEARN/nonebot-plugin-cupsprint plugins/nonebot-plugin-cupsprint
    ```

2. **环境依赖**：

    - **CUPS** (Common Unix Printing System)：用于打印管理。请确保已安装并启动 CUPS 服务。
    - **SANE** (Scanner Access Now Easy)：用于扫描管理。确保安装 `scanimage` 工具（通常与 `sane-utils` 一起安装）。

## 配置

在 NoneBot 的 `.env` 配置文件或其他配置文件中添加以下配置项：

```ini
# 打印和扫描权限设置
CUPSPRINT__GROUP_WHITELIST=["12345678"]         # 群聊白名单，可选
CUPSPRINT__PRIVATE_WHITELIST=["12345678"]       # 私聊白名单，可选
CUPSPRINT__GROUP_BLACKLIST=["12345678"]         # 群聊黑名单，可选
CUPSPRINT__PRIVATE_BLACKLIST=["12345678"]       # 私聊黑名单，可选

CUPSPRINT__PRINTER_NAME="Canon_MP280_series"    # 打印机名称，可选，不设置则使用默认打印机
CUPSPRINT__SCANNER_NAME="Canon_MP280_series"    # 扫描仪名称，可选，不设置则使用默认扫描仪

# 扫描配置
CUPSPRINT__SCAN_RESOLUTION=300                  # 默认扫描分辨率（DPI），可选
CUPSPRINT__SCAN_MODE="Color"                    # 扫描模式（Color、Gray、Lineart），可选
```

## 使用方法

1. **打印文件或图片**：

    - 回复消息并输入指令 `打印`，可将文件或图片发送至打印机。

2. **扫描图像**：
    - 输入指令 `扫描 [分辨率]` 触发扫描操作（如 `扫描 600`）。
    - 如果未指定分辨率，将使用配置文件中的默认分辨率。

## 示例

```plaintext
扫描 600          # 以 600 DPI 分辨率进行扫描
扫描              # 使用默认分辨率进行扫描
打印              # 回复要打印的文件或图片并发送
```

## 注意事项

-   确保运行 NoneBot 的用户有权限访问打印机和扫描仪设备。
