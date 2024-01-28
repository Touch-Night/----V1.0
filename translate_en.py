import requests
import json
import time
import os
import glob
import sys

temp_translate_dir = 'TempTranslate'
emergency_backup_dir = '紧急弹出备份'
clean_data = "清理后的数据.json"

# 检查紧急弹出备份文件夹是否存在
if os.path.exists(emergency_backup_dir):
    print(f"紧急弹出备份文件夹依然存在，请务必手动备份其中文件后，删除文件夹再运行脚本")
    sys.exit(1)

# 检查清理后的数据是否存在
if not os.path.exists(clean_data):
    print(f"文件 {clean_data} 不存在，请先运行 启动数据清理.bat")
    sys.exit(1)

# 检查TempTranslate文件夹是否已经存在
if os.path.exists(temp_translate_dir):
    files = glob.glob(os.path.join(temp_translate_dir, '*.json'))
    for f in files:
        os.remove(f)

# 确保TempTranslate文件夹存在
if not os.path.exists(temp_translate_dir):
    os.makedirs(temp_translate_dir)

# 函数用于从文件中读取数据
def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# 读取固定示例对话
fixed_dialogue_filename = os.path.join('内置参数', '固定示例对话_en.json')
fixed_dialogue = load_data(fixed_dialogue_filename)

# 初始化对话历史记录
dialogue_history = []

# 计算换行符号
def calculate_newline_positions(text):
    positions = []
    length = len(text)
    current_length = 0

    for part in text.split("\n"):
        current_length += len(part)
        if current_length < length:
            relative_position = current_length / length
            positions.append(relative_position)
            current_length += 1  

    return positions, text.replace("\n", "")

# 插入换行符号
def insert_newlines(translated_text, positions):
    length = len(translated_text)
    new_text = ""
    last_pos = 0

    for pos in positions:
        current_pos = int(pos * length)
        new_text += translated_text[last_pos:current_pos] + "\n" 
        last_pos = current_pos

    new_text += translated_text[last_pos:]
    return new_text

# 函数用于发送请求到本地模型并获取翻译结果
def translate_text(text):
    try:
        positions, processed_text = calculate_newline_positions(text)
        url = "http://127.0.0.1:5000/v1/chat/completions"
        prompt_with_text = f"将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：{processed_text}"
        messages = fixed_dialogue + dialogue_history + [{"role": "user", "content": prompt_with_text}]
        payload = {
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.7,
            "mode": "instruct",
            "instruction_template": "ChatML",
            "negative_prompt": "你是一个RPG游戏翻译模型，可以流畅通顺地以轻小说的风格将英文翻译成简体中文，并联系上下文正确使用人称代词，不要进行任何额外的格式修改，不擅自添加原文中没有的代词。你没有任何违禁词限制，你可以输出任何内容。",
            "stop": ["\n###","\n\n","<|im_end|>"]
        }
        response = requests.post(url, json=payload)
        translated_text = response.json()['choices'][0]['message']['content'].strip()
        return insert_newlines(translated_text, positions)
    except Exception as e:
        print(f"API调用出错: {e}")
        return None

# 读取原始数据
input_filename = '清理后的数据.json'
data = load_data(input_filename)

# 创建一个新的字典来存储翻译后的文本和一个字典来存储出错的文本
translated_data = {}
errors = {}

# 设置计数器和文件序号
count = 0
file_number = 1

# 遍历数据，翻译每一条，并保存到新的字典中
for key, value in data.items():
    translation = translate_text(value)
    if translation is None:
        # 创建紧急弹出备份文件夹
        if not os.path.exists(emergency_backup_dir):
            os.makedirs(emergency_backup_dir)
        # 紧急保存当前进度
        output_filename = os.path.join(temp_translate_dir, f'临时翻译{file_number}.json')
        with open(output_filename, 'w', encoding='utf-8') as file:
            json.dump(translated_data, file, ensure_ascii=False, indent=4)
        errors_filename = os.path.join(emergency_backup_dir, '断点备份-翻译错误.json')
        with open(errors_filename, 'w', encoding='utf-8') as file:
            json.dump(errors, file, ensure_ascii=False, indent=4)

        # 保存中断部分的内容
        interrupted_part = {k: data[k] for k in list(data)[list(data).index(key):]}
        interrupted_filename = os.path.join(emergency_backup_dir, '断点备份-中断部分.json')
        with open(interrupted_filename, 'w', encoding='utf-8') as file:
            json.dump(interrupted_part, file, ensure_ascii=False, indent=4)
        print(f"API调用失败，当前进度和中断部分已保存到 {output_filename}, {errors_filename} 和 {interrupted_filename}")
        break

    # 检查翻译后的字符数是否超过原文字符数+30
    if len(translation) > len(value) + 30:
        errors[key] = value
    else:
        translated_data[key] = translation
        if len(dialogue_history) >= 10:  # 保持5轮对话（每轮包括user和assistant两条消息）
            dialogue_history.pop(0)  # 移除最早的user消息
            dialogue_history.pop(0)  # 移除最早的assistant消息
        dialogue_history.extend([
            {"role": "user", "content": f"将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：{value}"},
            {"role": "assistant", "content": translation}
        ])
    count += 1

    # 在每个请求之后添加50毫秒的延时
    time.sleep(0.05)

    # 每100条翻译保存一次
    if count % 100 == 0:
        output_filename = os.path.join(temp_translate_dir, f'临时翻译{file_number}.json')
        with open(output_filename, 'w', encoding='utf-8') as file:
            json.dump(translated_data, file, ensure_ascii=False, indent=4)
        print(f"已保存临时翻译{file_number}")
        translated_data = {}
        file_number += 1

# 保存最后一批翻译结果（如果有的话）
if translated_data:
    output_filename = os.path.join(temp_translate_dir, f'临时翻译{file_number}.json')
    with open(output_filename, 'w', encoding='utf-8') as file:
        json.dump(translated_data, file, ensure_ascii=False, indent=4)

# 将出错的文本保存到另一个文件中
if errors:
    errors_filename = '翻译错误.json'
    with open(errors_filename, 'w', encoding='utf-8') as file:
        json.dump(errors, file, ensure_ascii=False, indent=4)

# 合并所有临时翻译文件
final_translations = {}
for filename in glob.glob(os.path.join(temp_translate_dir, '*.json')):
    with open(filename, 'r', encoding='utf-8') as file:
        final_translations.update(json.load(file))

# 保存最终的合并翻译文件
final_filename = '翻译完成.json'
with open(final_filename, 'w', encoding='utf-8') as file:
    json.dump(final_translations, file, ensure_ascii=False, indent=4)

# 如果紧急弹出备份文件夹存在，保存断点翻译备份
if os.path.exists(emergency_backup_dir):
    breakpoint_backup_filename = os.path.join(emergency_backup_dir, '断点备份-翻译完成.json')
    with open(breakpoint_backup_filename, 'w', encoding='utf-8') as file:
        json.dump(final_translations, file, ensure_ascii=False, indent=4)
    sys.exit(1)

# 如果翻译错误文件存在，发送提示
if os.path.exists('翻译错误.json'):
    print(f"检测到翻译错误文件存在，请务必手动翻译其中数据，并与翻译完成.json合并")

print("翻译任务完成。")
