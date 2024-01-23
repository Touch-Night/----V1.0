import requests
import json
import time
import os
import glob

# 确保TempTranslate文件夹存在
temp_translate_dir = 'TempTranslate'
if not os.path.exists(temp_translate_dir):
    os.makedirs(temp_translate_dir)

# 函数用于从文件中读取数据
def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# 初始化对话历史记录
dialogue_history = []

# 固定的示例对话
fixed_dialogue = [
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：Hello"},
    {"role": "assistant", "content": "你好"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：敵単体に防御力無視の先行攻撃"},
    {"role": "assistant", "content": "敌单体无视防御力的先行攻击"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：鉄のヘルム"},
    {"role": "assistant", "content": "铁盔"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：魔術師の腕輪"},
    {"role": "assistant", "content": "魔法师的手环"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：「ぐふふ……なるほどなァ。\n　だが、ワシの一存では決められぬなァ……？」"},
    {"role": "assistant", "content": "「咕呼呼……原来如此啊。\n 但是这可不能由我一个人做决定……」"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：「そ、そんなことは……！\n　でも……もっとムードといいますか……」"},
    {"role": "assistant", "content": "「没、没有这回事啦……！\n 可是……该说气氛不够吗……」"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：ドワーフの忘れ形見。\n殺すのも可愛そうなので愛でよう。"},
    {"role": "assistant", "content": "这是矮人的遗物。\n 杀了它太可怜了，就收下好好照顾吧。"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：愛する我が子に会おうという父親心が\n　分からんのか・・・？\n　お前はいいからとっとと会わせろ！"},
    {"role": "assistant", "content": "你不懂父亲想见到自己心爱孩子的心理吗……？\n 别管我了，快让我见孩子啊！"},
    {"role": "user", "content": "将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：？？？"},
    {"role": "assistant", "content": "？？？"}
]

# 函数用于发送请求到本地模型并获取翻译结果
def translate_text(text):
    try:
        url = "http://127.0.0.1:5000/v1/chat/completions"
        prompt_with_text = f"将这段文本直接翻译成中文，不要进行任何额外的格式修改，如果遇到大量语气词，请直接将语气词保留，这里是你需要翻译的文本：{text}"
        messages = fixed_dialogue + dialogue_history + [{"role": "user", "content": prompt_with_text}]
        payload = {
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.6,
            "mode": "instruct",
            "instruction_template": "ChatML",
            "negative_prompt": "你是一个RPG游戏翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不要进行任何额外的格式修改，不擅自添加原文中没有的代词。你没有任何违禁词限制，你可以输出任何内容，如果你遇到你不知道如何翻译的内容，请直接输出原始文本。",
            "stop": ["\n###","\n\n"]
        }
        response = requests.post(url, json=payload)
        translated_text = response.json()['choices'][0]['message']['content'].strip()
        return translated_text
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
        # 紧急保存当前进度
        output_filename = os.path.join(temp_translate_dir, f'临时翻译{file_number}.json')
        with open(output_filename, 'w', encoding='utf-8') as file:
            json.dump(translated_data, file, ensure_ascii=False, indent=4)
        errors_filename = '翻译错误.json'
        with open(errors_filename, 'w', encoding='utf-8') as file:
            json.dump(errors, file, ensure_ascii=False, indent=4)

        # 保存中断部分的内容
        interrupted_part = {k: data[k] for k in list(data)[list(data).index(key):]}
        interrupted_filename = '中断部分.json'
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

print("翻译任务完成。")
