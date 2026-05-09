import os
import importlib
import sys

class PluginManager:
    """插件管理器，负责加载和管理所有插件"""
    
    def __init__(self, app):
        self.app = app
        self.plugins = []
        self.plugin_dirs = [
            os.path.join(os.path.dirname(__file__), 'example_plugins'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_plugins')
        ]
    
    def load_plugins(self):
        """加载所有插件目录中的插件"""
        for plugin_dir in self.plugin_dirs:
            if os.path.exists(plugin_dir):
                self._load_plugins_from_dir(plugin_dir)
    
    def _load_plugins_from_dir(self, plugin_dir):
        """从指定目录加载插件"""
        # 将插件目录添加到sys.path
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)
        
        # 遍历目录中的所有py文件
        for filename in os.listdir(plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]  # 去掉.py后缀
                try:
                    # 导入模块
                    module = importlib.import_module(module_name)
                    
                    # 查找所有Plugin子类
                    for name in dir(module):
                        obj = getattr(module, name)
                        if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                            # 创建插件实例
                            plugin_instance = obj()
                            plugin_instance.initialize(self.app)
                            self.plugins.append(plugin_instance)
                            print(f"Loaded plugin: {plugin_instance.get_name()} v{plugin_instance.get_version()}")
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")
    
    def get_plugins(self):
        """获取所有已加载的插件"""
        return self.plugins
    
    def get_plugin_by_name(self, name):
        """根据名称获取插件"""
        for plugin in self.plugins:
            if plugin.get_name() == name:
                return plugin
        return None
    
    def trigger_time_update(self, current_time):
        """通知所有插件时间更新"""
        for plugin in self.plugins:
            try:
                plugin.on_time_update(current_time)
            except Exception as e:
                print(f"Error in {plugin.get_name()} on_time_update: {e}")
    
    def trigger_weather_update(self, weather_data):
        """通知所有插件天气更新"""
        for plugin in self.plugins:
            try:
                plugin.on_weather_update(weather_data)
            except Exception as e:
                print(f"Error in {plugin.get_name()} on_weather_update: {e}")
    
    def cleanup(self):
        """清理所有插件"""
        for plugin in self.plugins:
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"Error cleaning up {plugin.get_name()}: {e}")

# 导入Plugin基类
from .plugin_base import Plugin