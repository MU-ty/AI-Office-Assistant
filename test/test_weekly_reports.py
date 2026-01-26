"""
周报生成功能测试脚本
测试所有API端点的基本功能
"""

import httpx
import asyncio
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8002/api"

# 测试数据
TEST_LOG_DATA = {
    "work_type": "编码开发",
    "task_description": "完成用户认证模块的实现",
    "hours_spent": 6.5
}

TEST_LOG_DATA_2 = {
    "work_type": "文档编写",
    "task_description": "编写API文档和使用指南",
    "hours_spent": 2.0
}

TEST_REPORT_DATA = {
    "title": "2025年第4周工作总结",
    "week_start_date": (datetime.now() - timedelta(days=datetime.now().weekday())).isoformat(),
    "week_end_date": (datetime.now() + timedelta(days=6 - datetime.now().weekday())).isoformat()
}


async def test_weekly_reports_api():
    """测试周报API所有端点"""
    
    print("=" * 60)
    print("开始周报生成功能测试")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. 测试创建工作日志
            print("\n[1] 测试创建工作日志...")
            log_response = await client.post(
                f"{BASE_URL}/weekly_reports/logs",
                json=TEST_LOG_DATA
            )
            print(f"状态码: {log_response.status_code}")
            if log_response.status_code == 201:
                log_data = log_response.json()
                log_id = log_data["id"]
                print(f"✅ 创建工作日志成功")
                print(f"   日志ID: {log_id}")
                print(f"   工作类型: {log_data['work_type']}")
                print(f"   工时: {log_data['hours_spent']}小时")
            else:
                print(f"❌ 创建工作日志失败: {log_response.text}")
                return
            
            # 2. 创建第二条日志
            print("\n[2] 创建第二条工作日志...")
            log_response_2 = await client.post(
                f"{BASE_URL}/weekly_reports/logs",
                json=TEST_LOG_DATA_2
            )
            if log_response_2.status_code == 201:
                log_id_2 = log_response_2.json()["id"]
                print(f"✅ 创建成功，日志ID: {log_id_2}")
            else:
                print(f"❌ 创建失败: {log_response_2.text}")
            
            # 3. 测试获取日志列表
            print("\n[3] 测试获取工作日志列表...")
            list_response = await client.get(
                f"{BASE_URL}/weekly_reports/logs",
                params={"skip": 0, "limit": 10}
            )
            if list_response.status_code == 200:
                list_data = list_response.json()
                print(f"✅ 获取日志列表成功")
                print(f"   总数: {list_data['total']}")
                print(f"   显示数量: {len(list_data['items'])}")
            else:
                print(f"❌ 获取日志列表失败: {list_response.text}")
            
            # 4. 测试获取单个日志详情
            print(f"\n[4] 测试获取日志详情 (ID: {log_id})...")
            detail_response = await client.get(f"{BASE_URL}/weekly_reports/logs/{log_id}")
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print(f"✅ 获取日志详情成功")
                print(f"   任务描述: {detail_data['task_description']}")
            else:
                print(f"❌ 获取日志详情失败: {detail_response.text}")
            
            # 5. 测试更新日志
            print(f"\n[5] 测试更新日志 (ID: {log_id})...")
            update_response = await client.put(
                f"{BASE_URL}/weekly_reports/logs/{log_id}",
                json={"hours_spent": 7.0, "task_description": "更新后的任务描述"}
            )
            if update_response.status_code == 200:
                print(f"✅ 更新日志成功")
                print(f"   新工时: {update_response.json()['hours_spent']}小时")
            else:
                print(f"❌ 更新日志失败: {update_response.text}")
            
            # 6. 测试生成周报
            print("\n[6] 测试生成周报...")
            report_response = await client.post(
                f"{BASE_URL}/weekly_reports/",
                json=TEST_REPORT_DATA
            )
            print(f"状态码: {report_response.status_code}")
            if report_response.status_code == 201:
                report_data = report_response.json()
                report_id = report_data["id"]
                print(f"✅ 生成周报成功")
                print(f"   周报ID: {report_id}")
                print(f"   周期: {report_data['week']}")
                print(f"   总工时: {report_data['total_hours']}小时")
                print(f"   状态: {report_data['status']}")
                print(f"   摘要: {report_data['summary'][:100]}...")
            else:
                print(f"❌ 生成周报失败: {report_response.text}")
                return
            
            # 7. 测试获取周报列表
            print("\n[7] 测试获取周报列表...")
            reports_list = await client.get(
                f"{BASE_URL}/weekly_reports/",
                params={"skip": 0, "limit": 10}
            )
            if reports_list.status_code == 200:
                list_data = reports_list.json()
                print(f"✅ 获取周报列表成功")
                print(f"   总数: {list_data['total']}")
                print(f"   显示数量: {len(list_data['items'])}")
            else:
                print(f"❌ 获取周报列表失败: {reports_list.text}")
            
            # 8. 测试获取周报详情
            print(f"\n[8] 测试获取周报详情 (ID: {report_id})...")
            detail_response = await client.get(f"{BASE_URL}/weekly_reports/{report_id}")
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print(f"✅ 获取周报详情成功")
                print(f"   标题: {detail_data['title']}")
                print(f"   内容: {detail_data['content'] or '(未填写)'}")
            else:
                print(f"❌ 获取周报详情失败: {detail_response.text}")
            
            # 9. 测试更新周报
            print(f"\n[9] 测试更新周报 (ID: {report_id})...")
            update_response = await client.put(
                f"{BASE_URL}/weekly_reports/{report_id}",
                json={
                    "summary": "更新的摘要信息",
                    "content": "本周完成了用户认证模块的开发和测试"
                }
            )
            if update_response.status_code == 200:
                print(f"✅ 更新周报成功")
            else:
                print(f"❌ 更新周报失败: {update_response.text}")
            
            # 10. 测试提交周报
            print(f"\n[10] 测试提交周报审核 (ID: {report_id})...")
            submit_response = await client.post(
                f"{BASE_URL}/weekly_reports/{report_id}/submit"
            )
            if submit_response.status_code == 200:
                print(f"✅ 提交周报成功")
                print(f"   新状态: {submit_response.json()['status']}")
            else:
                print(f"❌ 提交周报失败: {submit_response.text}")
            
            # 11. 测试审核周报
            print(f"\n[11] 测试审核周报 (ID: {report_id})...")
            review_response = await client.post(
                f"{BASE_URL}/weekly_reports/{report_id}/review",
                json={
                    "status": "approved",
                    "review_feedback": "很好的工作总结"
                }
            )
            if review_response.status_code == 200:
                print(f"✅ 审核周报成功")
                print(f"   新状态: {review_response.json()['status']}")
            else:
                print(f"❌ 审核周报失败: {review_response.text}")
            
            # 12. 测试导出为Markdown
            print(f"\n[12] 测试导出周报为Markdown (ID: {report_id})...")
            export_response = await client.post(
                f"{BASE_URL}/weekly_reports/{report_id}/export",
                params={"format": "markdown"}
            )
            if export_response.status_code == 200:
                export_data = export_response.json()
                print(f"✅ 导出成功 (格式: {export_data['format']})")
                print(f"   内容预览:\n{export_data['content'][:200]}...")
            else:
                print(f"❌ 导出失败: {export_response.text}")
            
            # 13. 测试导出为HTML
            print(f"\n[13] 测试导出周报为HTML (ID: {report_id})...")
            export_response = await client.post(
                f"{BASE_URL}/weekly_reports/{report_id}/export",
                params={"format": "html"}
            )
            if export_response.status_code == 200:
                export_data = export_response.json()
                print(f"✅ 导出成功 (格式: {export_data['format']})")
                print(f"   内容预览:\n{export_data['content'][:200]}...")
            else:
                print(f"❌ 导出失败: {export_response.text}")
            
            # 14. 测试删除日志
            print(f"\n[14] 测试删除日志 (ID: {log_id})...")
            delete_response = await client.delete(f"{BASE_URL}/weekly_reports/logs/{log_id}")
            if delete_response.status_code == 204:
                print(f"✅ 删除日志成功")
            else:
                print(f"❌ 删除日志失败: {delete_response.text}")
            
            print("\n" + "=" * 60)
            print("✅ 所有测试完成！")
            print("=" * 60)
        
        except httpx.ConnectError:
            print("\n❌ 连接失败: 无法连接到服务器")
            print("请确保后端服务器运行在 http://localhost:8000")
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")


if __name__ == "__main__":
    print("周报生成功能测试脚本")
    print("确保后端服务器运行在 http://localhost:8000\n")
    asyncio.run(test_weekly_reports_api())
