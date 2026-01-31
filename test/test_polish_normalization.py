"""
学术润色模块测试和演示脚本
展示如何使用学术规范化服务
"""

import asyncio
import sys
import os
from pathlib import Path

# 设置编码 - 解决Windows中文编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径 - 指向backend目录
project_root = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

from app.services.polish_normalization_service import AcademicNormalizationService


def print_section(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demonstrate_terminology_check():
    """演示术语检查"""
    print_section("2.3.3.1 学术术语替换演示")
    
    service = AcademicNormalizationService()
    
    test_texts = [
        "这个研究超级好，我们的团队非常努力。",
        "怎么样解决这个问题呢？",
        "可以看出，我们做了很多事情。",
    ]
    
    for text in test_texts:
        print(f"\n[原文] {text}")
        issues = service.check_terminology(text)
        
        if issues:
            print(f"[OK] 发现 {len(issues)} 个术语问题:")
            for issue in issues:
                print(f"  * 原文: '{issue['original']}'")
                print(f"    建议: '{issue['suggested']}'")
                print(f"    原因: {issue['reason']}")
                print(f"    置信度: {issue['confidence']:.2f}")
        else:
            print("  无术语问题")


def demonstrate_tense_check():
    """演示时态检查"""
    print_section("2.3.3.2 时态调整演示")
    
    service = AcademicNormalizationService()
    
    test_texts = [
        "在进行着实验，结果很显著。",
        "正在计算着数据呢。",
        "我们一直在做这个研究啊。",
    ]
    
    for text in test_texts:
        print(f"\n[原文] {text}")
        issues = service.check_tense(text)
        
        if issues:
            print(f"[OK] 发现 {len(issues)} 个时态问题:")
            for issue in issues:
                print(f"  * 原文: '{issue['original']}'")
                print(f"    建议: '{issue['suggested']}'")
                print(f"    原因: {issue['reason']}")
        else:
            print("  无时态问题")


def demonstrate_style_check():
    """演示风格一致性检查"""
    print_section("2.3.3.3 风格一致性检查演示")
    
    service = AcademicNormalizationService()
    
    test_texts = [
        "数据显示第1个样本...第二个样本...第三个样本。",
        "参考文献等等 (et al.) 等等信息。",
        "结果包括No.1项、第2项、第三项。",
    ]
    
    for text in test_texts:
        print(f"\n[原文] {text}")
        issues = service.check_style_consistency(text)
        
        if issues:
            print(f"[OK] 发现 {len(issues)} 个风格问题:")
            for issue in issues:
                print(f"  * 位置: {issue['start']}-{issue['end']}")
                print(f"    原文: '{issue['original']}'")
                print(f"    问题: {issue['reason']}")
        else:
            print("  无风格问题")


def demonstrate_thesis_check():
    """演示论文规范检查"""
    print_section("2.3.3.4 学位论文规定检查演示")
    
    service = AcademicNormalizationService()
    
    test_texts = [
        "我们的研究表明这个方法很好。笔者认为这样做是对的。",
        "可以看出，这个结果显然是正确的。",
        "根据作者Smith说，这个理论是对的。",
    ]
    
    for text in test_texts:
        print(f"\n[原文] {text}")
        issues = service.check_thesis_requirements(text)
        
        if issues:
            print(f"[OK] 发现 {len(issues)} 个论文规范问题:")
            for issue in issues:
                print(f"  * 原文: '{issue['original']}'")
                print(f"    建议: {issue['suggested']}")
                print(f"    严重程度: {issue['severity']}")
                print(f"    置信度: {issue['confidence']:.2f}")
        else:
            print("  无论文规范问题")


def demonstrate_full_analysis():
    """演示完整分析"""
    print_section("完整的学术规范化分析演示")
    
    service = AcademicNormalizationService()
    
    text = """我们的研究进行了详细分析。这样做很好，超级有意思。
    
在进行着实验，结果显示第1个数据...第二个数据...等等。
根据作者说，可以看出这个方法应该是对的呢。
笔者认为这个结论非常重要，所以需要进一步研究。
"""
    
    print(f"\n[分析文本] (长度: {len(text)} 字符):\n")
    print(text)
    print("\n" + "-" * 70)
    
    # 执行分析
    analysis_result = service.analyze_text(text)
    
    # 生成报告
    report = service.generate_report(analysis_result)
    print(report)
    
    # 显示详细问题
    print(f"\n[详细问题列表]")
    print("-" * 70)
    
    all_issues = (
        analysis_result["terminology_issues"] +
        analysis_result["tense_issues"] +
        analysis_result["style_issues"] +
        analysis_result["thesis_issues"]
    )
    
    for i, issue in enumerate(all_issues, 1):
        print(f"\n{i}. [{issue['type'].upper()}] {issue['severity'].upper()}")
        print(f"   位置: {issue['start']}-{issue['end']}")
        print(f"   原文: {issue['original']}")
        print(f"   建议: {issue['suggested']}")
        print(f"   原因: {issue['reason']}")
        print(f"   规则: {issue['rule_id']}")
        print(f"   置信度: {issue['confidence']:.2f}")


def demonstrate_auto_fix():
    """演示自动修复"""
    print_section("自动修复演示")
    
    service = AcademicNormalizationService()
    
    text = "我们的研究进行了分析。这样做很好。"
    
    print(f"\n[原始文本]\n{text}\n")
    
    # 分析
    analysis_result = service.analyze_text(text)
    all_issues = (
        analysis_result["terminology_issues"] +
        analysis_result["tense_issues"] +
        analysis_result["style_issues"] +
        analysis_result["thesis_issues"]
    )
    
    print(f"发现 {len(all_issues)} 个问题")
    
    # 自动修复
    fixed_text, fixed_count = service.apply_fixes(text, all_issues, auto_fix_threshold=0.80)
    
    print(f"\n[修复后的文本]\n{fixed_text}\n")
    print(f"修复数量: {fixed_count} / {len(all_issues)}")
    print(f"修复准确率: {fixed_count / len(all_issues) * 100:.1f}%")


def demonstrate_confidence_filter():
    """演示置信度过滤"""
    print_section("置信度过滤演示")
    
    service = AcademicNormalizationService()
    
    text = "我们的研究表明这个结果很好。"
    
    print(f"\n[分析文本] {text}\n")
    
    # 分析
    analysis_result = service.analyze_text(text)
    all_issues = (
        analysis_result["terminology_issues"] +
        analysis_result["tense_issues"] +
        analysis_result["style_issues"] +
        analysis_result["thesis_issues"]
    )
    
    print("所有检测到的问题:")
    for issue in all_issues:
        print(f"  * {issue['original']} -> {issue['suggested']}")
        print(f"    置信度: {issue['confidence']:.2f}")
    
    # 不同置信度阈值的修复
    for threshold in [0.70, 0.80, 0.90, 0.95]:
        high_confidence_issues = [
            i for i in all_issues 
            if i.get("confidence", 0) >= threshold
        ]
        print(f"\n置信度 >= {threshold}: {len(high_confidence_issues)} 个问题可修复")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  学术润色模块 - 学术规范化服务演示")
    print("  Version: 1.0.0")
    print("=" * 70)
    
    # 运行各项演示
    demonstrate_terminology_check()
    demonstrate_tense_check()
    demonstrate_style_check()
    demonstrate_thesis_check()
    demonstrate_full_analysis()
    demonstrate_auto_fix()
    demonstrate_confidence_filter()
    
    # 总结
    print_section("演示完成")
    print("""
[SUCCESS] 学术规范化服务演示完毕

关键功能：
  [1] 术语替换 - 检查非正式术语并提出学术替代词
  [2] 时态调整 - 调整不规范的时态表达
  [3] 风格一致 - 检查格式、缩写等的一致性
  [4] 论文规范 - 检查学位论文的规范要求

使用场景：
  * 学位论文写作辅助
  * 学术文章质量检查
  * 学术出版社初审
  * 文献翻译质量控制
  * 写作教学与反馈

更多信息，请参考:
  [指南] POLISH_MODULE_GUIDE.md - 详细的使用指南
  [API] API 文档 - http://localhost:8000/api/docs
    """)


if __name__ == "__main__":
    main()
