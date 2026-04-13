@echo off
echo 🏢 企业知识库 SaaS - 部署脚本
echo ================================

echo 🚀 启动服务...
docker-compose up -d

echo.
echo ✅ 部署成功！
echo 📱 访问地址: http://localhost:8501
echo.
echo 停止服务: docker-compose down
pause