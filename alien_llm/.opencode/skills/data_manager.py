"""
Alien Signal Generator 数据管理技能
"""
import json
import os
from pathlib import Path

class DataManager:
    def __init__(self):
        import os
        # 使用绝对路径以确保在任何工作目录下都能找到数据文件
        base_path = os.path.join(os.path.dirname(__file__), "..", "..")
        self.signals_file = os.path.join(base_path, "signals", "nfc_info.json")
        self.planets_file = os.path.join(base_path, "signals", "planet_info.json")
        self.raw_data_file = os.path.join(base_path, "Raw_Data", "Raw.json")
    
    def load_signals(self):
        """加载信号数据"""
        if os.path.exists(self.signals_file):
            with open(self.signals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_signals(self, data):
        """保存信号数据"""
        with open(self.signals_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_planets(self):
        """加载星球数据"""
        if os.path.exists(self.planets_file):
            with open(self.planets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_planets(self, data):
        """保存星球数据"""
        with open(self.planets_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def validate_signals_format(self):
        """验证信号数据格式"""
        signals = self.load_signals()
        
        required_fields = ["id", "name", "signal_type", "structure_tags", 
                          "semantic_tags", "inference_tags", "knowledge_domain"]
        
        valid = True
        for i, signal in enumerate(signals):
            for field in required_fields:
                if field not in signal:
                    print(f"信号 {i} 缺少字段: {field}")
                    valid = False
        
        return valid
    
    def validate_planets_format(self):
        """验证星球数据格式"""
        planets = self.load_planets()
        
        required_fields = ["id", "name", "signal_type", "structure_tags", 
                          "semantic_tags", "inference_tags", "knowledge_domain",
                          "civilization_type", "perception_style", "technology_level"]
        
        valid = True
        for i, planet in enumerate(planets):
            for field in required_fields:
                if field not in planet:
                    print(f"星球 {i} 缺少字段: {field}")
                    valid = False
        
        return valid
    
    def add_signal(self, signal_data):
        """添加新信号"""
        signals = self.load_signals()
        signals.append(signal_data)
        self.save_signals(signals)
        print(f"已添加信号: {signal_data['name']}")
    
    def add_planet(self, planet_data):
        """添加新星球"""
        planets = self.load_planets()
        planets.append(planet_data)
        self.save_planets(planets)
        print(f"已添加星球: {planet_data['name']}")
    
    def get_signals_summary(self):
        """获取信号数据摘要"""
        signals = self.load_signals()
        summary = {
            "total_signals": len(signals),
            "signal_types": list(set(s["signal_type"] for s in signals)),
            "knowledge_domains": list(set(s["knowledge_domain"] for s in signals))
        }
        return summary
    
    def get_planets_summary(self):
        """获取星球数据摘要"""
        planets = self.load_planets()
        summary = {
            "total_planets": len(planets),
            "civilization_types": list(set(p["civilization_type"] for p in planets)),
            "perception_styles": list(set(p["perception_style"] for p in planets))
        }
        return summary

# 便捷函数
def validate_all_data():
    """验证所有数据格式"""
    dm = DataManager()
    print("验证信号数据格式...")
    signals_valid = dm.validate_signals_format()
    print("验证星球数据格式...")
    planets_valid = dm.validate_planets_format()
    
    return signals_valid and planets_valid

def get_data_summary():
    """获取数据摘要"""
    dm = DataManager()
    signals_summary = dm.get_signals_summary()
    planets_summary = dm.get_planets_summary()
    
    print("=== 信号数据摘要 ===")
    print(f"总信号数: {signals_summary['total_signals']}")
    print(f"信号类型: {signals_summary['signal_types']}")
    print(f"知识领域: {signals_summary['knowledge_domains']}")
    
    print("\n=== 星球数据摘要 ===")
    print(f"总星球数: {planets_summary['total_planets']}")
    print(f"文明类型: {planets_summary['civilization_types']}")
    print(f"感知风格: {planets_summary['perception_styles']}")

if __name__ == "__main__":
    print("Alien Signal Generator 数据管理工具")
    get_data_summary()