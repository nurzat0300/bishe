#!/usr/bin/env python3
"""
启动脚本 - 链路状态路由协议分布式仿真系统
"""
import sys
import os
import site

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _set_qt_plugin_paths():
    """固定 Qt 插件路径，避免平台插件加载失败。"""
    if os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH"):
        return

    # 优先从 site-packages 推断 PyQt5 插件路径
    candidate_bases = []
    try:
        candidate_bases.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        candidate_bases.append(site.getusersitepackages())
    except Exception:
        pass

    # 再从 Python 安装目录推断
    base_dir = os.path.dirname(sys.executable)
    candidate_bases.append(os.path.join(base_dir, "Lib", "site-packages"))

    for base in candidate_bases:
        plugins_path = os.path.join(base, "PyQt5", "Qt5", "plugins")
        if os.path.isdir(plugins_path):
            os.environ.setdefault("QT_PLUGIN_PATH", plugins_path)
            platforms_path = os.path.join(plugins_path, "platforms")
            if os.path.isdir(platforms_path):
                os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", platforms_path)
            return

_set_qt_plugin_paths()

from src.simulator import RoutingSimulator, main

if __name__ == '__main__':
    sys.exit(main())
