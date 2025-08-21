import os
import json
import logging
from tqdm import tqdm

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_json_files(directory, whitelisted_dirs):
    """
    在白名单指定的子目录中递归查找所有JSON文件。
    """
    json_files = []
    # 先遍历白名单目录
    for dir_name in whitelisted_dirs:
        path = os.path.join(directory, dir_name)
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.json'):
                        json_files.append(os.path.join(root, file))
    return json_files

def process_json_file(file_path):
    """
    处理单个JSON文件，提取诗词数据。
    根据 chinese-poetry 项目的结构，JSON文件可能是包含多个诗词对象的列表，
    也可能是单个诗词对象。
    """
    poems = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 检查数据是列表还是单个字典
            if isinstance(data, list):
                for item in data:
                    poem = extract_poem_data(item)
                    if poem:
                        poems.append(poem)
            elif isinstance(data, dict):
                poem = extract_poem_data(data)
                if poem:
                    poems.append(poem)
                    
    except json.JSONDecodeError:
        logging.warning(f"无法解析JSON文件: {file_path}")
    except Exception as e:
        logging.error(f"处理文件 {file_path} 时出错: {e}")
        
    return poems

def extract_poem_data(item):
    """从单个JSON对象中提取并格式化诗词数据"""
    if not isinstance(item, dict):
        return None

    # 尝试从不同的键提取内容，以兼容多种格式
    title = item.get('title', item.get('rhythmic', '无题'))
    author = item.get('author', '佚名')
    
    # 内容可能是 'paragraphs' (列表) 或 'content' (字符串)
    content_list = item.get('paragraphs', [])
    if not content_list and 'content' in item:
        # 如果 content 是字符串，按换行符分割
        if isinstance(item['content'], str):
            content_list = item['content'].split('\n')
        elif isinstance(item['content'], list):
            content_list = item['content']

    # 清理内容，去除空行和多余空格
    cleaned_content = [line.strip() for line in content_list if line.strip()]
    
    if title and author and cleaned_content:
        return {
            'title': title,
            'author': author,
            'content': cleaned_content
        }
    return None

def consolidate_poetry(
    source_directory='chinese-poetry-master/chinese-poetry-master',
    output_file='poetry_knowledge_base.json'
):
    """
    整合诗词数据。
    :param source_directory: 包含诗词JSON文件的源目录。
    :param output_file: 输出的整合后的知识库文件。
    """
    logging.info(f"开始从 '{source_directory}' 整合诗词数据...")
    
    # 定义只包含诗词的目录白名单（更完整的版本）
    whitelisted_dirs = [
        '全唐诗',
        '唐诗',
        '宋词',
        '元曲',
        '诗经',
        '楚辞',
        '五代诗词',
        '五代的词',
        '御定全唐詩',
        '曹操诗集',
        '纳兰性德',
        '千家诗',
        '水墨唐诗'
    ]
    
    # 1. 在白名单目录中查找JSON文件
    json_files = find_json_files(source_directory, whitelisted_dirs)
    if not json_files:
        logging.warning(f"在 '{source_directory}' 中未找到任何JSON文件。")
        return
        
    logging.info(f"找到 {len(json_files)} 个JSON文件，开始处理...")
    
    # 2. 加载现有知识库（如果存在），用于去重
    existing_poems = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                # 创建一个以 (标题, 作者) 为键的字典，便于快速查找
                for poem in existing_data:
                    key = (poem.get('title'), poem.get('author'))
                    existing_poems[key] = poem
            logging.info(f"已加载 {len(existing_poems)} 首现有诗词。")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"加载现有知识库 '{output_file}' 失败: {e}")
            # 如果文件损坏，可以选择备份并重新开始
            # os.rename(output_file, f"{output_file}.bak")
            # existing_poems = {}

    # 3. 处理所有找到的JSON文件
    all_new_poems = []
    for file_path in tqdm(json_files, desc="处理JSON文件"):
        all_new_poems.extend(process_json_file(file_path))
        
    logging.info(f"从新文件中提取了 {len(all_new_poems)} 首诗词。")
    
    # 4. 合并新旧数据并去重
    merged_poems_dict = existing_poems.copy()
    added_count = 0
    for poem in tqdm(all_new_poems, desc="合并与去重"):
        key = (poem.get('title'), poem.get('author'))
        if key not in merged_poems_dict:
            merged_poems_dict[key] = poem
            added_count += 1
            
    logging.info(f"合并完成。新增 {added_count} 首不重复的诗词。")
    
    # 5. 将最终结果写回文件
    final_poem_list = list(merged_poems_dict.values())
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_poem_list, f, ensure_ascii=False, indent=2)
        logging.info(f"成功将 {len(final_poem_list)} 首诗词保存到 '{output_file}'。")
    except IOError as e:
        logging.error(f"保存整合后的知识库失败: {e}")

if __name__ == '__main__':
    # 确保在正确的目录下运行
    # 这里的 'chinese-poetry-master' 目录应该与此脚本在同一层级
    consolidate_poetry()
