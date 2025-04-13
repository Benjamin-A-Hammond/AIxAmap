# run.py - 方便的启动脚本
import os
import sys
import subprocess
from pathlib import Path

def run_server():
    """
    智能启动FastAPI服务器，自动判断使用哪个入口文件
    """
    # 检查main.py是否存在
    if Path("main.py").exists():
        print("🚀 使用main.py启动服务器...")
        cmd = ["uvicorn", "main:app", "--reload"]
    # 检查api/index.py是否存在
    elif Path("api/index.py").exists():
        print("🚀 使用api.index:app启动服务器...")
        cmd = ["uvicorn", "api.index:app", "--reload"]
    else:
        print("❌ 错误：找不到入口文件。请确保main.py或api/index.py文件存在。")
        sys.exit(1)
    
    # 运行uvicorn服务器
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器时出错：{e}")
        sys.exit(1)

if __name__ == "__main__":
    # 检查环境变量
    required_vars = ["OPENAI_API_KEY", "AMAP_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ 警告：以下环境变量未设置：{', '.join(missing_vars)}")
        print("请确保.env文件存在并包含必要的API密钥")
        
        # 检查.env文件
        if not Path(".env").exists():
            print("❌ .env文件不存在。正在创建示例文件...")
            with open(".env", "w") as f:
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                f.write("AMAP_API_KEY=your_amap_api_key_here\n")
                f.write("AMAP_JS_API_KEY=your_amap_js_api_key_here\n")
                f.write("AMAP_JS_API_PWD=your_amap_js_security_code_here\n")
            print("✅ 已创建.env文件模板。请编辑该文件填入你的API密钥，然后重新运行此脚本。")
            sys.exit(1)
    
    # 启动服务器
    run_server()