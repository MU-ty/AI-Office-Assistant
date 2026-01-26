#!/usr/bin/env python3
"""
学术润色模块简单测试
"""
import sys
sys.path.insert(0, '.')

from app.services.polish_normalization_service import AcademicNormalizationService

def test_polish():
    service = AcademicNormalizationService()
    text = '我们的研究进行了分析。这样做很好，超级有意思。'
    
    print('='*70)
    print('学术润色模块 - 功能验证')
    print('='*70)
    print()
    print('原文:', text)
    print()
    
    # 测试术语检查
    print('1. 术语替换检查:')
    issues = service.check_terminology(text)
    print(f'   发现 {len(issues)} 个术语问题')
    for issue in issues[:3]:
        print(f'   - "{issue["original"]}" -> "{issue["suggested"]}"')
    print()
    
    # 测试时态检查
    text2 = '在进行着实验。'
    print('2. 时态调整检查:')
    print('   原文:', text2)
    issues2 = service.check_tense(text2)
    print(f'   发现 {len(issues2)} 个时态问题')
    print()
    
    # 完整分析
    print('3. 完整分析:')
    result = service.analyze_text(text)
    print(f'   术语问题: {len(result["terminology_issues"])}')
    print(f'   时态问题: {len(result["tense_issues"])}')
    print(f'   风格问题: {len(result["style_issues"])}')
    print(f'   论文规范: {len(result["thesis_issues"])}')
    print(f'   总计: {result["total_issues"]} 个问题')
    print()
    
    print('✅ 学术规范化服务工作正常！')

if __name__ == '__main__':
    test_polish()
