import datetime
from io import BytesIO
from pathlib import Path
import subprocess

import nonebot
from nonebot import get_plugin_config, on_command, logger
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Event,
    GroupMessageEvent,
    PrivateMessageEvent,
    MessageSegment,
    Message,
)

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-cupsprint",
    description="一个支持文件打印和扫描的 NoneBot 插件，支持自定义分辨率和扫描模式",
    usage=(
        "使用方法：\n"
        "1. 回复 '打印' 来打印文件或图片\n"
        "2. 输入 '扫描 [分辨率]' 进行扫描（分辨率可选，默认为配置中的默认值）\n"
        "插件支持设置扫描模式、分辨率、扫描区域等参数"
    ),
    type="application",
    homepage="https://github.com/zHElEARN/nonebot-plugin-cupsprint",
    config=Config,
    supported_adapters={"~onebot.v11"},
)


config = get_plugin_config(Config).cupsprint

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)


def download_file(url: str, filename: str) -> str | None:
    file_path = f"/tmp/{filename}"
    try:
        subprocess.run(
            ["curl", "-L", "--insecure", "-o", file_path, url],
            check=True,
            capture_output=True,
            text=True,
        )

        logger.info(f"下载文件成功: {file_path}")
        return file_path
    except subprocess.CalledProcessError as e:
        logger.error(f"下载文件失败: {e}")
        return None


def is_authorized(event: Event) -> bool:
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        if config.group_whitelist and group_id not in config.group_whitelist:
            return False
        if config.group_blacklist and group_id in config.group_blacklist:
            return False

    if isinstance(event, PrivateMessageEvent):
        user_id = str(event.user_id)
        if config.private_whitelist and user_id not in config.private_whitelist:
            return False
        if config.private_blacklist and user_id in config.private_blacklist:
            return False

    return True


async def get_file_path_from_event(event: Event) -> str | None:
    if not event.reply:
        return None

    message = event.reply.message
    for segment in message:
        if segment.type == "image":
            image_url = segment.data["url"]
            logger.info(f"图片链接: {image_url}")
            return download_file(image_url, "image_to_print.jpg")
        elif segment.type == "file":
            response = await nonebot.get_bot().get_file(file_id=segment.data["file_id"])
            file_path = response["url"].replace(
                "/app/.config/", "/home/zhelearn/services/napcat/"
            )
            logger.info(f"文件路径: {file_path}")
            return file_path
    return None


print_command = on_command(
    "打印", aliases={"打印文件", "打印图片", "print"}, rule=to_me()
)
scan_command = on_command(
    "扫描", aliases={"扫描文件", "扫描图片", "scan"}, rule=to_me()
)


@print_command.handle()
async def handle_print(event: Event):
    if not isinstance(event, (GroupMessageEvent, PrivateMessageEvent)):
        return

    if not is_authorized(event):
        await print_command.finish("您没有权限执行打印操作。")
        return

    file_path = await get_file_path_from_event(event)
    if not file_path:
        await print_command.finish("请回复要打印的文件或图片。")
        return

    lp_command = ["lp"]
    if config.printer_name:
        lp_command.extend(["-d", config.printer_name])
    lp_command.append(file_path)

    try:
        subprocess.run(lp_command, check=True)
        await print_command.finish("已将文件发送至打印机。")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to print file: {e}")
        await print_command.finish("打印失败，请检查打印机设置。")


@scan_command.handle()
async def handle_scan(event: Event, arg: Message = CommandArg()):
    if not isinstance(event, (GroupMessageEvent, PrivateMessageEvent)):
        return

    if not is_authorized(event):
        await scan_command.finish("您没有权限执行扫描操作。")
        return

    user_resolution = None
    if arg:
        try:
            user_resolution = int(arg.extract_plain_text().strip())
        except ValueError:
            await scan_command.finish("分辨率无效，请输入有效的数字。")

    resolution = user_resolution if user_resolution else config.scan_resolution

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/tmp/scan_{timestamp}.jpg"

    scanimage_command = ["scanimage", "--format", "jpeg", "--output-file", output_path]
    if config.scanner_name:
        scanimage_command.extend(["-d", config.scanner_name])

    scanimage_command.extend(["--resolution", str(resolution)])
    scanimage_command.extend(["--mode", config.scan_mode])

    try:
        subprocess.run(scanimage_command, check=True)
        logger.info(f"扫描成功，文件保存于: {output_path}")

        with open(output_path, "rb") as image_file:
            image_bytes = image_file.read()

        await scan_command.finish(MessageSegment.image(BytesIO(image_bytes)))
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to scan file: {e}")
        await scan_command.finish("扫描失败，请检查扫描仪设置。")
