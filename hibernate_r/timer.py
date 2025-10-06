# hibernate_r/timer.py

import threading
import time

import online_player_api as lib_online_player
from mcdreforged.api.all import *

from hibernate_r.config import Config


class TimerManager:
    def __init__(self, config: Config):
        self.current_timer = None
        self.config = config

    def start_timer(self, server: PluginServerInterface, stop_server):
        self.cancel_timer(server)

        time.sleep(2)

        wait_min = self.config.wait_min
        blacklist_player = self.config.blacklist_player

        player_list = lib_online_player.get_player_list()

        player_list = [
            player for player in player_list
            if player not in blacklist_player
        ]

        player_num = len(player_list)

        server.logger.info(f"当前在线玩家数量：{player_num}，黑名单玩家：{blacklist_player}")

        if player_num == 0:
            self.current_timer = threading.Timer(wait_min * 60, stop_server, [server])
            self.current_timer.start()
            server.logger.info("休眠倒计时开始")

    def cancel_timer(self, server: PluginServerInterface):
        if self.current_timer is not None:
            self.current_timer.cancel()
            self.current_timer = None
            server.logger.info("休眠倒计时取消")
