"""
台湾食品标签合规检查器
"""
from typing import Dict, List, Optional
from loguru import logger


class RepackageDesigner:
    """转包装设计合规指南"""

    # 台湾食品标签强制要求
    REQUIRED_FIELDS = {
        "品名": "产品名称",
        "净重": "重量",
        "内容量": "内容量",
        "原产地": "原产地(台湾或进口国)",
        "厂商名称": "制造商/进口商名称",
        "厂商地址": "制造商/进口商地址",
        "有效日期": "生产日期/到期日期",
        "保存条件": "储存方式",
        "营养成分": "营养成分表",
        "过敏原提示": "过敏原信息(如含有花生、牛奶等)",
    }

    TAIWAN_FOOD_REGULATIONS = {
        "label_language": "繁体中文",
        "metric_system": "公制单位(克、公斤、毫升、公升)",
        "allergen_format": "需明确标注过敏原",
        "nutrition_table": "必须标注热量、蛋白质、脂肪、碳水化合物、糖、钠",
        "origin_marking": "大陆产品需标注'大陆生产'或'中国大陆'",
        "health_claims": "不得声称医疗功效",
        "irradiation": "辐照食品需标注'辐照处理'",
    }

    def __init__(self):
        self.checklist = []

    def generate_packaging_spec(self, product: Dict) -> Dict:
        """生成包装规格说明"""
        spec = {
            "product_name": product.get("name", ""),
            "recommended_name": self._generate_taiwan_name(product.get("name", "")),
            "label_specifications": self._generate_label_spec(product),
            "required_elements": self._get_required_elements(product),
            "prohibited_claims": self._get_prohibited_claims(),
            "design_notes": self._get_design_notes(product),
            "compliance_checklist": self._create_checklist(product),
        }
        return spec

    def _generate_taiwan_name(self, original_name: str) -> str:
        """生成符合台湾市场的产品名称"""
        # 转换风格
        replacements = {
            "富硒米": "富硒营养米",
            "功能米": "机能米",
            "降糖": "低GI",
            "荞麦面": "蕎麥麵",
            "全麦": "全麥",
            "有机": "有機",
        }

        name = original_name
        for cn, tw in replacements.items():
            name = name.replace(cn, tw)

        # 附加品牌标识
        if "健康" not in name and "有机" not in name:
            name = "健康" + name

        return name

    def _generate_label_spec(self, product: Dict) -> Dict:
        """生成标签规格"""
        return {
            "正面": {
                "品名": "{{产品名称}}",
                "净重": "{{重量}}",
                "品牌标志": "{{品牌}}",
                "产品图片": "高清实物图",
                "特色卖点": "如：有机认证、无添加",
            },
            "背面": {
                "营养成分表": "每100公克含量",
                "原产地": "中国大陆",
                "进口商信息": "台湾进口商名称、地址、电话",
                "有效日期": "西元年/月/日",
                "保存条件": "常温保存、避免潮湿",
                "过敏原提示": "本产品含有XX过敏原",
            },
            "侧面": {
                "产品说明": "产品特点介绍(繁中)",
                "食用建议": "建议食用量、方法",
                "营养声称": "如：高纤维、低钠",
            },
        }

    def _get_required_elements(self, product: Dict) -> List[str]:
        """获取必需元素清单"""
        elements = [
            "品名（繁体中文）",
            "净重或内容量（公制单位）",
            "原产地标注",
            "台湾进口商名称及地址",
            "台湾进口商电话",
            "有效日期（清楚标示）",
            "保存条件或方法",
            "营养成分表",
            "过敏原信息",
            "批号（生产批次）",
        ]

        # 根据产品类型添加特定要求
        category = product.get("category", "")
        if "米" in category:
            elements.append("碾制日期")
            elements.append("食米来源（稻米种类）")
        if "面" in category:
            elements.append("成分表（面粉来源）")

        return elements

    def _get_prohibited_claims(self) -> List[str]:
        """获取禁止声称清单"""
        return [
            "疗效声称：不得声称'治疗'、'预防疾病'",
            "医疗用语：不得使用'降低血糖'、'改善心血管'等医疗用语",
            "夸大宣传：不得使用'最'、'第一'等绝对化用语",
            "营养声称：需符合台湾营养声称规范",
            "认证伪造：不得伪造有机认证等标志",
            "辐照食品：需标注辐照处理",
        ]

    def _get_design_notes(self, product: Dict) -> Dict:
        """获取设计注意事项"""
        return {
            "字体要求": {
                "品名": "字号≥2mm",
                "内容物重": "字号≥1.2mm",
                "厂商信息": "字号≥1.2mm",
            },
            "颜色要求": "文字需清晰可读，对比度足够",
            "图案要求": "不得使用国旗、地图等敏感图案",
            "翻译要求": "所有中文需为繁体字",
            "条码要求": "需有台湾可识读条码(EAN/UPC)",
            "包装材质": "需符合台湾食品容器包装卫生标准",
        }

    def _create_checklist(self, product: Dict) -> List[Dict]:
        """创建合规检查清单"""
        items = [
            {"item": "品名为繁体中文", "status": "pending", "note": ""},
            {"item": "重量使用公制单位", "status": "pending", "note": ""},
            {"item": "原产地标注清楚", "status": "pending", "note": ""},
            {"item": "进口商信息完整", "status": "pending", "note": ""},
            {"item": "有效日期标示清楚", "status": "pending", "note": ""},
            {"item": "营养成分表完整", "status": "pending", "note": ""},
            {"item": "无禁止声称内容", "status": "pending", "note": ""},
            {"item": "包装材质检验合格", "status": "pending", "note": ""},
            {"item": "条码可正常扫描", "status": "pending", "note": ""},
            {"item": "标签审核通过", "status": "pending", "note": ""},
        ]
        return items

    def export_packaging_requirements(self, products: List[Dict]) -> str:
        """导出包装要求文档"""
        report = """# 台湾进口食品包装要求指南

## 一、标签强制要求

"""
        for field, desc in self.REQUIRED_FIELDS.items():
            report += f"- **{field}**：{desc}\n"

        report += """
## 二、营养成分标注规范

必须标注以下项目（每100公克或100毫升）：
- 热量
- 蛋白质
- 脂肪
- 饱和脂肪
- 反式脂肪
- 碳水化合物
- 糖
- 钠

## 三、过敏原标注

以下过敏原必须明确标注：
- 含有麸质的谷类（小麦、大麦、黑麦等）
- 甲壳类动物
- 蛋类
- 鱼类
- 花生
- 大豆
- 乳制品
- 坚果类
- 浓度≥10 mg/kg的亚硫酸盐

## 四、禁止声称

1. 医疗功效声称
2. 夸大不实广告
3. 伪造认证标志
4. 绝对化用语（最、第一等）

## 五、产品列表

"""
        for product in products:
            spec = self.generate_packaging_spec(product)
            report += f"""### {spec['product_name']}
- 建议名称：{spec['recommended_name']}
- 必需元素：{len(spec['required_elements'])}项
- 合规状态：待审核

"""

        return report
