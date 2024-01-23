@echo off
chcp 65001
echo 正在运行 自动翻译 脚本...
cd %~dp0
python translate.py
echo 请务必检查翻译内容 如果翻译 错误文件.json 内存在数据 请将其手动翻译后 手动将其增加到 翻译完成.json 内 
echo 如果出现Text Generation Webui异常 或者api异常等 导致翻译中断 
echo 脚本将会自动生成 中断部分.json 文件 您可以在备份当前翻译完成数据后 手动将中断文件重命名为 清理后的数据.json
echo 然后重新运行 自动翻译.bat 
pause

