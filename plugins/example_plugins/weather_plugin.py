from plugins.plugin_base import Plugin

class WeatherPlugin(Plugin):
    """天气插件 - 扩展天气功能"""
    
    def __init__(self):
        super().__init__()
        self.name = "Weather Plugin"
        self.version = "1.0.0"
        self.description = "扩展天气显示功能，包括空气质量和预报"
        self.author = "hellojint"
        self.weather_data = None
    
    def initialize(self, app):
        super().initialize(app)
        print(f"{self.name} initialized!")
    
    def on_weather_update(self, weather_data):
        """天气更新时处理数据"""
        self.weather_data = weather_data
        print(f"[{self.name}] Weather updated: {weather_data}")
        # 可以在这里添加更多天气处理逻辑
    
    def get_air_quality(self):
        """模拟获取空气质量"""
        return "良好 (AQI: 45)"
    
    def get_forecast(self):
        """模拟获取天气预报"""
        return ["明天: 晴天 25°C", "后天: 多云 23°C", "大后天: 小雨 20°C"]