# ==================================================
# 导入模块
# ==================================================
import yaml
import aiohttp
from loguru import logger
from app.tools.path_utils import *
from app.tools.settings_access import readme_settings

# ==================================================
# 更新工具函数
# ==================================================


async def get_metadata_info_async():
    """
    异步获取 metadata.yaml 文件信息

    Returns:
        dict: metadata.yaml 文件的内容，如果读取失败则返回 None
    """
    try:
        # 获取更新检查 URL
        update_check_url = get_update_check_url()
        logger.debug(f"从网络获取 metadata.yaml: {update_check_url}")

        # 发送异步请求
        async with aiohttp.ClientSession() as session:
            async with session.get(update_check_url, timeout=10) as response:
                response.raise_for_status()  # 检查请求是否成功
                content = await response.text()

                # 解析 YAML 内容
                metadata = yaml.safe_load(content)
                logger.debug(f"成功从网络读取 metadata.yaml 文件: {metadata}")
                return metadata
    except Exception as e:
        logger.error(f"从网络获取 metadata.yaml 文件失败: {e}")
        return None


def get_metadata_info():
    """
    获取 metadata.yaml 文件信息（同步版本）

    Returns:
        dict: metadata.yaml 文件的内容，如果读取失败则返回 None
    """
    try:
        # 使用 asyncio 运行异步函数
        import asyncio

        return asyncio.run(get_metadata_info_async())
    except Exception as e:
        logger.error(f"同步获取 metadata.yaml 文件失败: {e}")
        return None


async def get_latest_version_async(channel=None):
    """
    获取最新版本信息（异步版本）

    Args:
        channel (str, optional): 更新通道，默认为 None，此时会从设置中读取
        0: 稳定通道(release), 1: 测试通道(beta), 2: 发布预览通道

    Returns:
        dict: 包含版本号和版本号数字的字典，格式为 {"version": str, "version_no": int}
    """
    try:
        # 如果没有指定通道，从设置中读取
        if channel is None:
            channel = readme_settings("update", "update_channel")

        # 获取 metadata 信息（异步）
        metadata = await get_metadata_info_async()
        if not metadata:
            return None

        # 根据通道获取对应的版本信息
        channel_map = {
            0: "release",  # 稳定通道
            1: "beta",  # 测试通道
            2: "alpha",  # 发布预览通道
        }

        channel_name = channel_map.get(channel, "release")
        latest = metadata.get("latest", {})
        latest_no = metadata.get("latest_no", {})

        version = latest.get(channel_name, "")
        version_no = latest_no.get(channel_name, 0)

        logger.debug(
            f"获取最新版本信息成功: 通道={channel_name}, 版本={version}, 版本号={version_no}"
        )
        return {"version": version, "version_no": version_no}
    except Exception as e:
        logger.error(f"获取最新版本信息失败: {e}")
        return None


def get_latest_version(channel=None):
    """
    获取最新版本信息（同步版本）

    Args:
        channel (str, optional): 更新通道，默认为 None，此时会从设置中读取
        0: 稳定通道(release), 1: 测试通道(beta), 2: 发布预览通道

    Returns:
        dict: 包含版本号和版本号数字的字典，格式为 {"version": str, "version_no": int}
    """
    try:
        # 使用 asyncio 运行异步函数
        import asyncio

        return asyncio.run(get_latest_version_async(channel))
    except Exception as e:
        logger.error(f"获取最新版本信息失败: {e}")
        return None


def get_update_source_url():
    """
    获取更新源 URL

    Returns:
        str: 更新源 URL，如果获取失败则返回默认值
    """
    try:
        # 从设置中读取更新源
        update_source = readme_settings("update", "update_source")

        # 更新源映射
        source_map = {
            0: "https://github.com",  # GitHub
            1: "https://ghfast.top",  # ghfast
            2: "https://gh-proxy.com",  # gh-proxy
        }

        source_url = source_map.get(update_source, "https://github.com")
        logger.debug(f"获取更新源 URL 成功: {source_url}")
        return source_url
    except Exception as e:
        logger.error(f"获取更新源 URL 失败: {e}")
        return "https://github.com"


def compare_versions(current_version, latest_version):
    """
    比较版本号

    Args:
        current_version (str): 当前版本号，格式为 "vX.X.X.X"
        latest_version (str): 最新版本号，格式为 "vX.X.X.X"

    Returns:
        int: 1 表示有新版本，0 表示版本相同，-1 表示比较失败
    """
    try:
        # 移除版本号前缀 "v"
        current = current_version.lstrip("v")
        latest = latest_version.lstrip("v")

        # 分割版本号为列表
        current_parts = list(map(int, current.split(".")))
        latest_parts = list(map(int, latest.split(".")))

        # 比较版本号
        for i in range(max(len(current_parts), len(latest_parts))):
            current_part = current_parts[i] if i < len(current_parts) else 0
            latest_part = latest_parts[i] if i < len(latest_parts) else 0

            if latest_part > current_part:
                return 1
            elif latest_part < current_part:
                return -1

        return 0
    except Exception as e:
        logger.error(f"比较版本号失败: {e}")
        return -1


async def get_update_file_name_async(version, arch="x64", struct="dir"):
    """
    获取更新文件名（异步版本）

    Args:
        version (str): 版本号，格式为 "vX.X.X.X"
        arch (str, optional): 架构，默认为 "x64"
        struct (str, optional): 结构，默认为 "dir"

    Returns:
        str: 更新文件名
    """
    try:
        metadata = await get_metadata_info_async()
        if not metadata:
            # 如果 metadata 读取失败，使用默认格式
            name_format = "SecRandom-Windows-[version]-[arch]-[struct].zip"
        else:
            name_format = metadata.get(
                "name_format", "SecRandom-Windows-[version]-[arch]-[struct].zip"
            )

        # 替换占位符
        file_name = name_format.replace("[version]", version)
        file_name = file_name.replace("[arch]", arch)
        file_name = file_name.replace("[struct]", struct)

        logger.debug(f"生成更新文件名成功: {file_name}")
        return file_name
    except Exception as e:
        logger.error(f"生成更新文件名失败: {e}")
        return f"SecRandom-Windows-{version}-{arch}-{struct}.zip"


def get_update_file_name(version, arch="x64", struct="dir"):
    """
    获取更新文件名（同步版本）

    Args:
        version (str): 版本号，格式为 "vX.X.X.X"
        arch (str, optional): 架构，默认为 "x64"
        struct (str, optional): 结构，默认为 "dir"

    Returns:
        str: 更新文件名
    """
    try:
        # 使用 asyncio 运行异步函数
        import asyncio

        return asyncio.run(get_update_file_name_async(version, arch, struct))
    except Exception as e:
        logger.error(f"生成更新文件名失败: {e}")
        return f"SecRandom-Windows-{version}-{arch}-{struct}.zip"


def get_github_repo_url():
    """
    获取 GitHub 仓库 URL

    Returns:
        str: GitHub 仓库 URL
    """
    return "https://github.com/Anwen-OVO/SecRandom"


def get_update_check_url():
    """
    获取更新检查 URL

    Returns:
        str: 更新检查 URL
    """
    source_url = get_update_source_url()
    repo_url = get_github_repo_url()
    # 替换 GitHub 域名为更新源域名
    update_check_url = (
        repo_url.replace("https://github.com", source_url) + "/raw/main/metadata.yaml"
    )
    logger.debug(f"生成更新检查 URL 成功: {update_check_url}")
    return update_check_url
