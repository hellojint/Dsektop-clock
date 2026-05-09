from plugins.plugin_base import Plugin

class WorldClockPlugin(Plugin):
    """世界时钟插件 - 显示更多时区时间"""
    
    def __init__(self):
        super().__init__()
        self.name = "World Clock Plugin"
        self.version = "1.0.0"
        self.description = "显示更多城市的时间"
        self.author = "hellojint"
    
    def initialize(self, app):
        super().initialize(app)
        print(f"{self.name} initialized!")
    
    def on_time_update(self, current_time):
        """时间更新时输出日志"""
        print(f"[{self.name}] Current time: {current_time}")
    
    def get_menu_items(self):
        """返回菜单项"""
        return [
            {
                "label": "世界时钟设置",
                "command": self.show_settings
            }
        ]
    
    def show_settings(self):
        """显示插件设置"""
        print(f"{self.name} settings opened!")