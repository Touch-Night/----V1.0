@echo off
chcp 65001
echo 正在运行 自动翻译 脚本...
echo 翻译日语请使用Sakura模型，翻译英语请使用Qwen模型 
set /p language="请输入需要被翻译的主要语言 (日语输入1，英语输入2)："
if /i "%language%"=="1" goto jp
if /i "%language%"=="2" goto en
goto invalid

:jp
echo 正在运行translate_jp脚本...
cd %~dp0
python translate_jp.py

if errorlevel 1 (
    goto :end
)

echo 请务必检查翻译完成.json内的内容 
goto :end

:en
echo 正在运行translate_en脚本...
cd %~dp0
python translate_en.py

if errorlevel 1 (
    goto :end
)

echo 请务必检查翻译完成.json内的内容 
goto :end

:invalid
echo 无效的语言输入
echo 请重新输入有效的语言
pause>nul
goto start

:end
pause

