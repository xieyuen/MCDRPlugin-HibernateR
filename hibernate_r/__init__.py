#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from mcdreforged.api.all import *

from .FakeServer import FakeServerSocket
from .byte_utils import *
from .config import Config, load_config
from .timer import TimerManager

# 创建 TimerManager 实例
timer_manager = TimerManager()
# 创建 fake_server_socket 实例
fake_server_socket: FakeServerSocket | None = None
# 预期的服务器状态
wish_server_status: bool = True
# 插件配置
config: Config


# 初始化插件
def on_load(server: PluginServerInterface, _prev_module):
    global fake_server_socket, wish_server_status, config

    # 构建命令树
    builder = SimpleCommandBuilder()
    builder.command('!!hr sleep', lambda src: hr_sleep(src.get_server()))
    builder.command('!!hr wakeup', lambda src: hr_wakeup(src.get_server()))
    builder.command('!!hr wakeup fs', lambda src: fake_server_socket.start(src.get_server(), start_server))
    builder.register(server)

    # 检查并加载配置文件
    config = load_config(server)

    server.logger.info("参数初始化完成")

    # 创建 fake_server_socket 实例
    fake_server_socket = FakeServerSocket(server, config)

    # 检查服务器状态并启动计时器或伪装服务器
    if server.is_server_running() or server.is_server_startup():
        wish_server_status = True
        server.logger.info("服务器正在运行，启动计时器")
        timer_manager.start_timer(server, stop_server)
    else:
        server.logger.warning("无法判断当前服务器状态，请使用 !!hr start fs 手动启动伪装服务器")


def on_unload(server: PluginServerInterface):
    # 取消计时器
    timer_manager.cancel_timer(server)
    # 关闭伪装服务器
    fake_server_socket.stop(server)
    server.logger.info("插件已卸载")


# 手动休眠
@new_thread
def hr_sleep(server: PluginServerInterface):
    server.logger.info("事件：手动休眠")
    timer_manager.cancel_timer(server)
    stop_server(server)


# 手动唤醒
@new_thread
def hr_wakeup(server: PluginServerInterface):
    server.logger.info("事件：手动唤醒")
    if fake_server_socket.stop(server):
        start_server(server)
    else:
        server.logger.warning("伪装服务器关闭失败，无法手动唤醒")


# 服务器启动完成事件
@new_thread
def on_server_startup(server: PluginServerInterface):
    global wish_server_status
    wish_server_status = True
    server.logger.info("事件：服务器启动")
    time.sleep(5)
    timer_manager.start_timer(server, stop_server)


# 玩家加入事件
@new_thread
def on_player_joined(server: PluginServerInterface, _player, _info):
    server.logger.info("事件：玩家加入")
    timer_manager.cancel_timer(server)


# 玩家退出事件
@new_thread
def on_player_left(server: PluginServerInterface, _player):
    server.logger.info("事件：玩家退出")
    time.sleep(2)
    if server.is_server_running():
        timer_manager.start_timer(server, stop_server)


@new_thread
def on_server_stop(server: PluginServerInterface, _server_return_code: int):
    server.logger.info("事件：服务器关闭")
    timer_manager.cancel_timer(server)
    # 匹配预期状态
    if wish_server_status:
        server.logger.warning("意外的服务器关闭，不启动伪装服务器")
    else:
        fake_server_socket.start(server, start_server)


# 主动关闭服务器
def stop_server(server: PluginServerInterface):
    global wish_server_status
    wish_server_status = False
    server.stop()


# 主动开启服务器
def start_server(server: PluginServerInterface):
    global wish_server_status
    wish_server_status = True
    server.start()
