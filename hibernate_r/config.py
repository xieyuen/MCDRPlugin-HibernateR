from mcdreforged.api.all import *


class Config(Serializable):
    wait_min: int = 10
    blacklist_player: list = []
    ip: str = "0.0.0.0"
    port: int = 25565
    protocol: int = 2
    motd: list[str] = [
        "§e服务器正在休眠！",
        "§c进入服务器即可唤醒服务器"
    ]
    version_text: str = "§4Sleeping"
    kick_message: list[str] = [
        "§e§l请求成功！",
        "",
        "§f服务器正在启动！请稍作等待后进入"
    ]
    samples: list[str] = [
        "服务器正在休眠",
        "进入服务器以唤醒"
    ]
    server_icon: str = "server_icon.png"


default_config = Config.get_default()


def load_config(server: PluginServerInterface) -> Config:
    config = server.load_config_simple("HibernateR.json", target_class=Config, in_data_folder=False)

    if len(config.motd) != 2:
        server.logger.warning("MOTD字段长度错误，使用默认值覆盖")
        config.motd = default_config.motd
        server.save_config_simple(config, "HibernateR.json", in_data_folder=False)

    return config
