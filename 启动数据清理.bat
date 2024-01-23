@echo off
chcp 65001
echo 正在运行 数据清洗 脚本...
cd %~dp0
python clean.py
echo 数据清洗完成 清理后的数据已经创建
echo 注意 自动数据清理可能存在疏漏 请务必手动翻阅纠错

pause

