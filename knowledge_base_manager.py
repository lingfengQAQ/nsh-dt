import os
import json
import logging
import re
from collections import Counter
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KnowledgeBaseManager:
    def __init__(self, db_parts_directory='poetry_db_parts'):
        """
        初始化知识库管理器，支持从拆分的数据库文件加载。
        :param db_parts_directory: 包含拆分后知识库文件的目录。
        """
        self.db_parts_directory = db_parts_directory
        self.poetry_data_parts = []
        self.char_index = {}
        self.load_data_parts()
        self.build_index()

    def load_data_parts(self):
        """
        从指定目录加载所有拆分的知识库文件。
        """
        logging.info(f"开始从 '{self.db_parts_directory}' 目录加载知识库分片...")
        if not os.path.isdir(self.db_parts_directory):
            logging.error(f"知识库目录 '{self.db_parts_directory}' 不存在。")
            logging.error("请先运行 split_database.py 脚本来生成数据库分片。")
            return

        part_files = sorted([
            os.path.join(self.db_parts_directory, f)
            for f in os.listdir(self.db_parts_directory)
            if f.startswith('poetry_part_') and f.endswith('.json')
        ])

        if not part_files:
            logging.error(f"在 '{self.db_parts_directory}' 目录中未找到知识库分片文件。")
            return

        for file_path in part_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.poetry_data_parts.append(json.load(f))
                logging.info(f"成功加载分片: {os.path.basename(file_path)}")
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"加载分片 '{file_path}' 失败: {e}")
        
        total_poems = sum(len(part) for part in self.poetry_data_parts)
        logging.info(f"知识库加载完成，共加载 {len(self.poetry_data_parts)} 个分片，总计 {total_poems} 条记录。")

    def build_index(self):
        logging.info("正在构建索引...")
        for part_idx, part in enumerate(self.poetry_data_parts):
            for poem_idx, poem in enumerate(part):
                content = "".join(poem.get('content', []))
                for char in set(content):
                    if char not in self.char_index:
                        self.char_index[char] = []
                    self.char_index[char].append((part_idx, poem_idx))
        logging.info("索引构建完成。")

    def _search_in_part(self, data_part, char_pool_counts):
        """
        在单个数据分片中搜索诗句，返回包含完整诗歌和匹配诗句的字典。
        :return: 字典，格式为 {(title, author): (poem_object, [matched_clauses])}
        """
        found_poems_dict = {}
        for poem in data_part:
            content_list = poem.get('content', [])
            if isinstance(content_list, str):
                content_list = [content_list]

            matched_clauses = []
            for line in content_list:
                clauses = re.split(r'[，。？！,?!]', line)
                for clause in clauses:
                    clause = clause.strip()
                    if not clause:
                        continue

                    clean_clause = ''.join(c for c in clause if '\u4e00' <= c <= '\u9fff')
                    if not clean_clause or '□' in clause or len(clean_clause) < 5:
                        continue
                    
                    is_match = True
                    clause_counts = Counter(clean_clause)
                    for char, count in clause_counts.items():
                        if char_pool_counts.get(char, 0) < count:
                            is_match = False
                            break
                    
                    if is_match:
                        matched_clauses.append(clause)
            
            if matched_clauses:
                key = (poem.get('title', '无题'), poem.get('author', '佚名'))
                if key not in found_poems_dict:
                    found_poems_dict[key] = (poem, [])
                found_poems_dict[key][1].extend(matched_clauses)
                
        return found_poems_dict

    def find_poem_from_chars(self, chars):
        """
        使用索引从字符池中找到匹配的诗歌。
        :param chars: 包含可用汉字的字符串。
        :return: 包含 (poem_object, [matched_clauses]) 元组的列表，或 None。
        """
        if not self.poetry_data_parts:
            logging.warning("知识库为空，无法执行搜索。")
            return None

        char_pool_counts = Counter(c for c in chars if '\u4e00' <= c <= '\u9fff')
        if not char_pool_counts:
            return None

        candidate_poems = set()
        for char in char_pool_counts.keys():
            if char in self.char_index:
                for part_idx, poem_idx in self.char_index[char]:
                    candidate_poems.add((part_idx, poem_idx))

        final_results_dict = {}
        for part_idx, poem_idx in candidate_poems:
            poem = self.poetry_data_parts[part_idx][poem_idx]
            content_list = poem.get('content', [])
            if isinstance(content_list, str):
                content_list = [content_list]

            matched_clauses = []
            for line in content_list:
                clauses = re.split(r'[，。？！,?!]', line)
                for clause in clauses:
                    clause = clause.strip()
                    if not clause:
                        continue

                    clean_clause = ''.join(c for c in clause if '\u4e00' <= c <= '\u9fff')
                    if not clean_clause or '□' in clause or len(clean_clause) < 5:
                        continue
                    
                    is_match = True
                    clause_counts = Counter(clean_clause)
                    for char, count in clause_counts.items():
                        if char_pool_counts.get(char, 0) < count:
                            is_match = False
                            break
                    
                    if is_match:
                        matched_clauses.append(clause)
            
            if matched_clauses:
                key = (poem.get('title', '无题'), poem.get('author', '佚名'))
                if key not in final_results_dict:
                    final_results_dict[key] = (poem, [])
                final_results_dict[key][1].extend(matched_clauses)

        if not final_results_dict:
            return None
        
        return list(final_results_dict.values())
