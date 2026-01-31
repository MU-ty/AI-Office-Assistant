"""
学术规范化处理服务 - 核心业务逻辑
实现流程图中的2.3.3学术规范化子模块：
  2.3.3.1 学术术语替换
  2.3.3.2 时态调整
  2.3.3.3 风格一致性检查
  2.3.3.4 学位论文规定检查
"""

from typing import List, Dict, Optional, Tuple
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AcademicNormalizationService:
    """学术规范化处理服务"""
    
    def __init__(self):
        """初始化学术规范化服务"""
        # 2.3.3.1 学术术语替换规则
        self.terminology_replacements = {
            "非常": "显著",
            "很": "相当",
            "好": "优良",
            "说": "指出",
            "做": "实施",
            "看": "观察",
            "用": "采用",
            "可以": "能够",
            "可能": "或许",
            "里面": "内部",
            "下来": "",
            "而言": "来说",
            "的话": "",
            "对于": "关于",
        }
        
        # 学术术语库（反向替换：非学术术语 -> 学术术语）
        self.informal_to_formal = {
            "超级": "非常",
            "特别": "尤其",
            "老是": "始终",
            "怎么": "如何",
            "那么": "因此",
            "这样": "如此",
            "咋样": "怎样",
            "挺": "相当",
            "真": "确实",
            "可真": "实在",
        }
        
        # 2.3.3.2 时态调整规则
        self.tense_patterns = {
            # 检测非学术时态的正则模式
            "过去进行": r"(在|正在|不断).*?着",
            "非正式过去": r"(了|过|来着)",
            "非正式现在": r"(呢|啊|吧|嘛)",
        }
        
        # 2.3.3.3 风格一致性检查
        self.style_rules = {
            "单数复数": {
                "pattern": r"(\w+s\s+\w+s)",
                "description": "应该使用一致的单复数形式"
            },
            "缩写一致性": {
                "pattern": r"(etc\.|等等|ETC)",
                "description": "缩写形式需要一致"
            },
            "数字格式": {
                "pattern": r"(\d+个|\d+种|\d+次)",
                "description": "数字表示方式需要一致"
            }
        }
        
        # 2.3.3.4 学位论文规范检查
        self.thesis_rules = {
            "称谓规范": {
                "patterns": [
                    (r"我们?的研究", "建议改为：本研究"),
                    (r"本文的作者|我们的团队", "建议改为：本研究小组或课题组"),
                    (r"笔者认为", "建议改为：根据研究结果或相关文献"),
                ],
                "severity": "medium"
            },
            "表述规范": {
                "patterns": [
                    (r"可以看出|显然", "建议改为：研究表明或结果显示"),
                    (r"应该|必须|一定", "建议改为：应当或需要"),
                    (r"好的|不好的", "建议改为：良好的或不当的"),
                ],
                "severity": "medium"
            },
            "逻辑词规范": {
                "patterns": [
                    (r"所以|因此这|这样", "建议改为：因此或由此"),
                    (r"而且还有|同时并且", "建议改为：此外或同时"),
                ],
                "severity": "minor"
            },
            "引用规范": {
                "patterns": [
                    (r"根据.*?说", "建议完整引用格式：(Author Year)"),
                    (r"有人说|据说", "建议使用正式引用"),
                ],
                "severity": "major"
            }
        }

    # ================================================================
    # 2.3.3.1 学术术语替换
    # ================================================================
    
    def check_terminology(self, text: str) -> List[Dict]:
        """
        检查学术术语问题
        
        识别非学术用语并提出替换建议
        
        Args:
            text: 输入文本
            
        Returns:
            问题列表，每个问题包含位置、原文、建议、置信度等
        """
        issues = []
        
        # 检查非正式术语
        for informal, formal in self.informal_to_formal.items():
            pattern = r"\b" + informal + r"\b"
            for match in re.finditer(pattern, text):
                issue = {
                    "type": "terminology",
                    "severity": "minor",
                    "start": match.start(),
                    "end": match.end(),
                    "original": match.group(),
                    "suggested": formal,
                    "reason": f"将非正式术语'{informal}'替换为学术术语'{formal}'",
                    "confidence": 0.95,
                    "rule_id": "TERM_001"
                }
                issues.append(issue)
        
        # 检查常见错误术语
        common_errors = {
            "进行了": "进行",
            "进行来": "进行",
            "做了": "实施",
            "进行了分析": "分析了",
        }
        
        for error, correction in common_errors.items():
            pattern = r"\b" + re.escape(error) + r"\b"
            for match in re.finditer(pattern, text):
                issue = {
                    "type": "terminology",
                    "severity": "minor",
                    "start": match.start(),
                    "end": match.end(),
                    "original": match.group(),
                    "suggested": correction,
                    "reason": f"术语修正：'{error}' -> '{correction}'",
                    "confidence": 0.90,
                    "rule_id": "TERM_002"
                }
                issues.append(issue)
        
        return issues
    
    # ================================================================
    # 2.3.3.2 时态调整
    # ================================================================
    
    def check_tense(self, text: str) -> List[Dict]:
        """
        检查时态问题
        
        识别不规范的时态表达
        
        Args:
            text: 输入文本
            
        Returns:
            时态问题列表
        """
        issues = []
        
        # 检查进行时表达
        pattern = r"(在|正在|不断)\s*\S+着"
        for match in re.finditer(pattern, text):
            issue = {
                "type": "tense",
                "severity": "medium",
                "start": match.start(),
                "end": match.end(),
                "original": match.group(),
                "suggested": match.group().replace("着", ""),
                "reason": "学术文章应避免使用进行时，改用完成时或一般过去时",
                "confidence": 0.85,
                "rule_id": "TENSE_001"
            }
            issues.append(issue)
        
        # 检查非正式时态标记
        informal_tense = [
            (r"(了|过|来着)$", "过去式标记不规范"),
            (r"呢|啊|吧|嘛$", "非正式语气词"),
        ]
        
        sentences = re.split(r"[。！？]", text)
        for sent_idx, sentence in enumerate(sentences):
            for pattern, desc in informal_tense:
                if re.search(pattern, sentence.strip()):
                    start = sum(len(s) + 1 for s in sentences[:sent_idx])
                    issue = {
                        "type": "tense",
                        "severity": "minor",
                        "start": start,
                        "end": start + len(sentence),
                        "original": sentence.strip(),
                        "suggested": re.sub(pattern, "", sentence.strip()),
                        "reason": f"修正时态表达: {desc}",
                        "confidence": 0.80,
                        "rule_id": "TENSE_002"
                    }
                    issues.append(issue)
        
        return issues
    
    # ================================================================
    # 2.3.3.3 风格一致性检查
    # ================================================================
    
    def check_style_consistency(self, text: str) -> List[Dict]:
        """
        检查风格一致性
        
        检查表述方式、格式、缩写等是否一致
        
        Args:
            text: 输入文本
            
        Returns:
            风格问题列表
        """
        issues = []
        
        # 检查数字表示方式一致性
        number_patterns = [
            (r"第\d+个", "中文数字格式"),
            (r"No\.\d+", "英文格式"),
            (r"第\d+", "数字格式"),
        ]
        
        found_formats = {}
        for pattern, fmt_name in number_patterns:
            for match in re.finditer(pattern, text):
                if fmt_name not in found_formats:
                    found_formats[fmt_name] = []
                found_formats[fmt_name].append((match.start(), match.end(), match.group()))
        
        # 如果有多种格式混用，产生问题
        if len(found_formats) > 1:
            most_common = max(found_formats.items(), key=lambda x: len(x[1]))
            for fmt_name, matches in found_formats.items():
                if fmt_name != most_common[0]:
                    for start, end, text_match in matches:
                        issue = {
                            "type": "style",
                            "severity": "minor",
                            "start": start,
                            "end": end,
                            "original": text_match,
                            "suggested": f"统一为{most_common[0]}格式",
                            "reason": "数字表示格式应保持一致",
                            "confidence": 0.75,
                            "rule_id": "STYLE_001"
                        }
                        issues.append(issue)
        
        # 检查缩写一致性
        abbreviations = re.findall(r"etc|ETC|等等|et al|et al\.", text)
        if len(set(abbreviations)) > 1:
            for match in re.finditer(r"etc|ETC|等等|et al|et al\.", text):
                if match.group() != abbreviations[0]:
                    issue = {
                        "type": "style",
                        "severity": "minor",
                        "start": match.start(),
                        "end": match.end(),
                        "original": match.group(),
                        "suggested": abbreviations[0],
                        "reason": "缩写形式应保持一致",
                        "confidence": 0.80,
                        "rule_id": "STYLE_002"
                    }
                    issues.append(issue)
        
        return issues
    
    # ================================================================
    # 2.3.3.4 学位论文规定检查
    # ================================================================
    
    def check_thesis_requirements(self, text: str) -> List[Dict]:
        """
        检查学位论文规范
        
        根据学位论文规范检查用词、表述、引用格式等
        
        Args:
            text: 输入文本
            
        Returns:
            论文规范问题列表
        """
        issues = []
        
        # 检查各类规范
        for rule_type, rule_config in self.thesis_rules.items():
            severity = rule_config.get("severity", "medium")
            
            for pattern, suggestion in rule_config["patterns"]:
                for match in re.finditer(pattern, text):
                    issue = {
                        "type": "thesis",
                        "severity": severity,
                        "start": match.start(),
                        "end": match.end(),
                        "original": match.group(),
                        "suggested": suggestion,
                        "reason": f"{rule_type}规范: {suggestion}",
                        "confidence": 0.85 if severity == "major" else 0.80,
                        "rule_id": f"THESIS_{rule_type.upper()}"
                    }
                    issues.append(issue)
        
        return issues
    
    # ================================================================
    # 综合分析与处理
    # ================================================================
    
    def analyze_text(self, text: str) -> Dict:
        """
        综合分析文本，识别所有类型的学术规范问题
        
        Args:
            text: 输入文本
            
        Returns:
            包含所有问题类型的分析结果
        """
        logger.info(f"开始分析文本，长度: {len(text)} 字符")
        
        # 执行所有检查
        terminology_issues = self.check_terminology(text)
        tense_issues = self.check_tense(text)
        style_issues = self.check_style_consistency(text)
        thesis_issues = self.check_thesis_requirements(text)
        
        # 去重（相同位置的问题只保留置信度最高的）
        all_issues = terminology_issues + tense_issues + style_issues + thesis_issues
        unique_issues = self._deduplicate_issues(all_issues)
        
        # 按位置排序
        unique_issues.sort(key=lambda x: x["start"])
        
        # 统计
        result = {
            "terminology_issues": [i for i in unique_issues if i["type"] == "terminology"],
            "tense_issues": [i for i in unique_issues if i["type"] == "tense"],
            "style_issues": [i for i in unique_issues if i["type"] == "style"],
            "thesis_issues": [i for i in unique_issues if i["type"] == "thesis"],
            "total_issues": len(unique_issues),
            "by_severity": self._count_by_severity(unique_issues),
            "by_type": self._count_by_type(unique_issues),
        }
        
        logger.info(f"分析完成，发现 {len(unique_issues)} 个问题")
        return result
    
    def apply_fixes(self, text: str, issues: List[Dict], auto_fix_threshold: float = 0.85) -> Tuple[str, int]:
        """
        应用建议的修复
        
        根据置信度自动修复问题
        
        Args:
            text: 原始文本
            issues: 问题列表
            auto_fix_threshold: 自动修复的置信度阈值
            
        Returns:
            (修复后的文本, 修复数量)
        """
        # 按位置倒序排列，从后往前替换（避免位置偏移）
        sorted_issues = sorted(issues, key=lambda x: x["start"], reverse=True)
        
        fixed_count = 0
        modified_text = text
        
        for issue in sorted_issues:
            if issue.get("confidence", 0) >= auto_fix_threshold:
                start = issue["start"]
                end = issue["end"]
                suggestion = issue["suggested"]
                
                modified_text = modified_text[:start] + suggestion + modified_text[end:]
                fixed_count += 1
                logger.debug(f"已修复: {issue['original']} -> {suggestion}")
        
        return modified_text, fixed_count
    
    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """去重：同一位置的问题只保留置信度最高的"""
        if not issues:
            return issues
        
        grouped = {}
        for issue in issues:
            key = (issue["start"], issue["end"])
            if key not in grouped or issue.get("confidence", 0) > grouped[key].get("confidence", 0):
                grouped[key] = issue
        
        return list(grouped.values())
    
    def _count_by_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """统计各严重程度的问题数"""
        counts = {"minor": 0, "medium": 0, "major": 0}
        for issue in issues:
            severity = issue.get("severity", "medium")
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_by_type(self, issues: List[Dict]) -> Dict[str, int]:
        """统计各类型的问题数"""
        counts = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            counts[issue_type] = counts.get(issue_type, 0) + 1
        return counts
    
    def generate_report(self, analysis_result: Dict) -> str:
        """
        生成人类可读的分析报告
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            格式化的报告文本
        """
        report = []
        report.append("=" * 60)
        report.append("学术规范化分析报告")
        report.append("=" * 60)
        
        report.append(f"\n【问题统计】")
        report.append(f"  总问题数: {analysis_result['total_issues']}")
        report.append(f"  术语问题: {len(analysis_result['terminology_issues'])}")
        report.append(f"  时态问题: {len(analysis_result['tense_issues'])}")
        report.append(f"  风格问题: {len(analysis_result['style_issues'])}")
        report.append(f"  论文规范: {len(analysis_result['thesis_issues'])}")
        
        report.append(f"\n【严重程度分布】")
        for severity, count in analysis_result.get("by_severity", {}).items():
            report.append(f"  {severity}: {count} 个")
        
        report.append(f"\n【问题类型分布】")
        for issue_type, count in analysis_result.get("by_type", {}).items():
            report.append(f"  {issue_type}: {count} 个")
        
        return "\n".join(report)
