from pathlib import Path
import subprocess

import nonebot
from nonebot import get_plugin_config, on_command, logger
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent, PrivateMessageEvent

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot-cupsprint",
    description="A NoneBot plugin for printing files or images",
    usage="Reply with 'print' to print the file or image",
    config=Config,
)

config = get_plugin_config(Config).cupsprint

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)


def download_file(url: str, filename : str) -> str | None:
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
            file_path = response["url"].replace("/app/.config/", "/home/zhelearn/services/napcat/")
            logger.info(f"文件路径: {file_path}")
            return file_path
    return None


print_command = on_command(
    "打印", aliases={"打印文件", "打印图片", "print"}, rule=to_me()
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
