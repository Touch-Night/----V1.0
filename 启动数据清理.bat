@echo off
chcp 65001
set /p language="请输入需要被翻译的主要语言 (日语输入1，英语输入2)："
if /i "%language%"=="1" goto jp
if /i "%language%"=="2" goto en
goto invalid

:jp
echo 正在运行clean_jp脚本...
cd %~dp0
python clean_jp.py

if errorlevel 1 (
    goto :end
)

echo 日语清理完成
echo 注意 自动数据清理可能存在疏漏 请务必手动翻阅纠错
goto end

:en
echo 正在运行clean_en脚本...
cd %~dp0
python clean_en.py

if errorlevel 1 (
    goto :end
)

echo 英语清理完成
echo 注意 自动数据清理可能存在疏漏 请务必手动翻阅纠错
goto end

:invalid
echo 无效的语言输入
echo 请重新输入有效的语言
pause>nul
goto start

:end
pause

