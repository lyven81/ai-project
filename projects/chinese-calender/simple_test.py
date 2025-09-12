"""
简化的测试文件，用于验证基本API功能
"""

import requests
import time
import subprocess
import threading
import os
from datetime import date, timedelta

class APITester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.test_results = []
    
    def test_api(self, method, endpoint, json_data=None, expected_status=200, test_name=""):
        """通用API测试方法"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=json_data)
            elif method == "DELETE":
                response = requests.delete(url)
            
            success = response.status_code == expected_status
            result = {
                "test_name": test_name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response": response.json() if response.content else None
            }
            self.test_results.append(result)
            
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {test_name}: {method} {endpoint} -> {response.status_code}")
            
            return response
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "method": method,
                "endpoint": endpoint,
                "success": False,
                "error": str(e)
            }
            self.test_results.append(result)
            print(f"❌ {test_name}: {method} {endpoint} -> ERROR: {e}")
            return None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始API测试...\n")
        
        # 1. 健康检查
        self.test_api("GET", "/api/health", test_name="健康检查")
        
        # 2. 获取今日信息
        self.test_api("GET", "/api/days/today", test_name="获取今日信息")
        
        # 3. 获取特定日期
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.test_api("GET", f"/api/days/{tomorrow}", test_name="获取特定日期")
        
        # 4. 获取无效日期（应该返回400）
        self.test_api("GET", "/api/days/invalid-date", expected_status=400, test_name="无效日期格式")
        
        # 5. 获取吉日推荐
        self.test_api("GET", "/api/recommend?purpose=marriage&limit=3", test_name="结婚吉日推荐")
        
        # 6. 无效用途推荐（应该返回400）
        self.test_api("GET", "/api/recommend?purpose=invalid", expected_status=400, test_name="无效用途推荐")
        
        # 7. 获取用途列表
        self.test_api("GET", "/api/purposes", test_name="获取用途列表")
        
        # 8. 获取统计信息
        self.test_api("GET", "/api/stats", test_name="获取统计信息")
        
        # 9. 收藏功能测试
        test_user = "test_user_" + str(int(time.time()))
        favorite_data = {
            "user_id": test_user,
            "date_id": tomorrow,
            "purpose": "marriage",
            "remind_days_before": [7, 3, 1]
        }
        
        favorite_response = self.test_api("POST", "/api/favorites", json_data=favorite_data, test_name="创建收藏")
        
        # 10. 获取收藏列表
        self.test_api("GET", f"/api/favorites?user_id={test_user}", test_name="获取收藏列表")
        
        # 11. 设置提醒（如果收藏成功的话）
        if favorite_response and favorite_response.status_code == 200:
            favorite_id = favorite_response.json().get("id")
            reminder_data = {
                "user_id": test_user,
                "favorite_id": favorite_id,
                "remind_days_before": [5, 2]
            }
            self.test_api("POST", "/api/reminders/subscribe", json_data=reminder_data, test_name="设置提醒")
            
            # 12. 删除收藏
            self.test_api("DELETE", f"/api/favorites/{favorite_id}?user_id={test_user}", test_name="删除收藏")
        
        # 输出测试结果统计
        self.print_summary()
    
    def print_summary(self):
        """输出测试结果统计"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.get("success", False))
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 测试结果统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests} ✅")
        print(f"   失败: {failed_tests} ❌")
        print(f"   通过率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.test_results:
                if not result.get("success", False):
                    print(f"   - {result['test_name']}: {result.get('error', 'HTTP错误')}")

def start_server():
    """启动测试服务器"""
    print("🚀 启动测试服务器...")
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    # 等待服务器启动
    time.sleep(3)
    
    # 检查服务器是否启动成功
    try:
        response = requests.get("http://localhost:8080/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器启动成功!")
            return process
    except:
        pass
    
    print("❌ 服务器启动失败!")
    process.terminate()
    return None

def main():
    """主函数"""
    print("🎯 黄道吉日APP - API测试套件")
    print("=" * 50)
    
    # 启动服务器
    server_process = start_server()
    if not server_process:
        return
    
    try:
        # 运行测试
        tester = APITester()
        tester.run_all_tests()
    finally:
        # 关闭服务器
        print("\n🛑 关闭测试服务器...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()