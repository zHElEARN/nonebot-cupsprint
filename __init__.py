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
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)


def download_file(url, filename):
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


print_command = on_command("打印", aliases={"打印文件", "打印图片"}, rule=to_me())


@print_command.handle()
async def handle_print(event: Event):
    if not isinstance(event, (GroupMessageEvent, PrivateMessageEvent)):
        return

    if not event.reply:
        await print_command.finish("请回复要打印的文件或图片")
        return

    message = event.reply.message
    for segment in message:
        if segment.type == "image":
            image_url = segment.data["url"]
            logger.info(f"图片链接: {image_url}")

            image_path = download_file(image_url, "image_to_print.jpg")
            if image_path:
                subprocess.run(["lp", image_path], check=True)
                await print_command.finish("已将图片发送至打印机")

        elif segment.type == "file":
            response = await nonebot.get_bot().get_file(file_id=segment.data["file_id"])
            logger.info(f"response: {response}")

            path: str = response["url"]
            name = segment.data["file"]

            fixed_path = path.replace("/app/.config/", "/home/zhelearn/services/napcat/")

            logger.info(f"文件路径: {fixed_path}")
            logger.info(f"文件名: {name}")

            subprocess.run(["lp", fixed_path], check=True)
            await print_command.finish("已将文件发送至打印机")

        else:
            await print_command.finish("未检测到文件或图片")
