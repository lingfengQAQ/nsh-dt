import os
import json
import logging
import math

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def split_database(
    input_file='poetry_knowledge_base.json',
    output_dir='poetry_db_parts',
    num_parts=10
):
    """
    将大型JSON知识库文件拆分成多个较小的部分。

    :param input_file: 输入的知识库JSON文件。
    :param output_dir: 存放拆分后文件的目录。
    :param num_parts: 要拆分的份数。
    """
    logging.info(f"开始拆分知识库 '{input_file}'...")

    # 1. 检查输入文件是否存在
    if not os.path.exists(input_file):
        logging.error(f"输入文件 '{input_file}' 不存在。")
        return

    # 2. 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"已创建输出目录: {output_dir}")

    # 3. 读取完整的知识库
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            all_poems = json.load(f)
        logging.info(f"成功加载 {len(all_poems)} 首诗词。")
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"读取知识库文件 '{input_file}' 失败: {e}")
        return

    # 4. 计算每个部分的大小并进行拆分
    total_poems = len(all_poems)
    poems_per_part = math.ceil(total_poems / num_parts)
    
    logging.info(f"计划拆分为 {num_parts} 个部分，每个部分约 {poems_per_part} 首诗词。")

    for i in range(num_parts):
        start_index = i * poems_per_part
        end_index = start_index + poems_per_part
        
        # 获取当前部分的数据
        part_data = all_poems[start_index:end_index]
        
        if not part_data:
            logging.info(f"第 {i+1} 部分没有数据，停止拆分。")
            break
            
        # 定义输出文件名
        output_file_part = os.path.join(output_dir, f'poetry_part_{i+1}.json')
        
        # 写入文件
        try:
            with open(output_file_part, 'w', encoding='utf-8') as f:
                json.dump(part_data, f, ensure_ascii=False, indent=2)
            logging.info(f"成功保存部分 {i+1}/{num_parts} 到 '{output_file_part}' ({len(part_data)} 首)。")
        except IOError as e:
            logging.error(f"保存文件 '{output_file_part}' 失败: {e}")

    logging.info("知识库拆分完成。")

if __name__ == '__main__':
    split_database()
