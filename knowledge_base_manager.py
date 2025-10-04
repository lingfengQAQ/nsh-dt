import os
import sys
import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容打包后的环境）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境
    return os.path.join(os.path.abspath("."), relative_path)

class KnowledgeBaseManager:
    def __init__(self, db_path='poetry.db', json_path='../poetry_knowledge_base.json', parts_dir='../poetry_db_parts', sample_path='sample_poetry.json', clean_path='clean_poetry.json'):
        """
        初始化知识库管理器，支持多种数据源
        :param db_path: SQLite数据库路径
        :param json_path: JSON知识库路径
        :param parts_dir: 分片数据库目录
        :param sample_path: 示例数据文件路径
        :param clean_path: 清洁数据文件路径
        """
        # 统一使用模块所在目录作为相对路径的基准，确保无论从哪个工作目录启动都能找到数据文件
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # 使用 get_resource_path 处理打包后的路径
        self.db_path = get_resource_path(db_path) if not os.path.isabs(db_path) else db_path
        self.json_path = self._resolve_path(json_path)
        self.parts_dir = self._resolve_path(parts_dir)
        self.sample_path = self._resolve_path(sample_path)
        self.clean_path = self._resolve_path(clean_path)
        self.is_loaded = False
        self.poetry_data = []
        self._poem_cache = {}

        # 倒排索引：{字符: [(poem_idx, clause), ...]}
        self._char_index = {}
        self._index_built = False

        # 尝试不同的数据源
        self._load_data()

    def _load_data(self):
        """加载诗词数据，尝试多种数据源"""
        try:
            # 优先尝试SQLite数据库（最完整的数据）
            if self.db_path and os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 1000:
                if self._load_from_sqlite():
                    return

            # 尝试分片JSON文件
            if self.parts_dir and os.path.exists(self.parts_dir):
                if self._load_from_parts():
                    return

            # 尝试单个JSON文件
            if self.json_path and os.path.exists(self.json_path):
                if self._load_from_json():
                    return

            # 尝试清洁数据文件（备选）
            if self.clean_path and os.path.exists(self.clean_path):
                if self._load_from_clean():
                    return

            # 尝试示例数据文件（最后备选）
            if self.sample_path and os.path.exists(self.sample_path):
                if self._load_from_sample():
                    return

            logging.error("未找到可用的诗词数据库")

        except Exception as e:
            logging.error(f"加载诗词数据失败: {e}")

    def _load_from_sqlite(self):
        """从SQLite数据库加载"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            if not tables:
                logging.warning("SQLite数据库中没有找到表")
                conn.close()
                return False

            # 优先尝试poems表
            table_name = 'poems'
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                if count == 0:
                    raise Exception("poems表为空")
            except:
                # 如果poems表不存在或为空，尝试其他表
                for table_tuple in tables:
                    table_name = table_tuple[0]
                    if 'poems' in table_name.lower():
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                            count = cursor.fetchone()[0]
                            if count > 0:
                                break
                        except:
                            continue
                else:
                    logging.warning("未找到包含数据的表")
                    conn.close()
                    return False

            # 查询数据 - 根据表结构调整
            try:
                # 先检查列结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]

                logging.info(f"表 {table_name} 的列: {column_names}")

                # 根据列名构建查询
                if 'content' in column_names:
                    # 如果有content列，直接使用（读取全部数据）
                    cursor.execute(f"SELECT content FROM {table_name}")
                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            poem = json.loads(row[0])
                            self.poetry_data.append(poem)
                        except:
                            continue

                elif 'title' in column_names and 'author' in column_names:
                    # 如果有title和author列，构建数据（读取全部数据）
                    if 'paragraphs' in column_names:
                        cursor.execute(f"SELECT title, author, paragraphs FROM {table_name}")
                    else:
                        cursor.execute(f"SELECT title, author FROM {table_name}")

                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            title = row[0] or '无题'
                            author = row[1] or '佚名'

                            # 处理内容
                            if len(row) > 2 and row[2]:
                                try:
                                    paragraphs = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                                    content = paragraphs if isinstance(paragraphs, list) else [str(paragraphs)]
                                except:
                                    content = [str(row[2])]
                            else:
                                content = []

                            poem = {
                                'title': title,
                                'author': author,
                                'content': content
                            }
                            self.poetry_data.append(poem)
                        except Exception as e:
                            continue

            except Exception as e:
                logging.error(f"查询数据失败: {e}")
                conn.close()
                return False

            conn.close()

            if self.poetry_data:
                self.is_loaded = True
                logging.info(f"从SQLite加载了 {len(self.poetry_data)} 首诗词")
                return True

        except Exception as e:
            logging.error(f"SQLite加载失败: {e}")

        return False

    def _load_from_parts(self):
        """从分片JSON文件加载"""
        try:
            part_files = [f for f in os.listdir(self.parts_dir)
                         if f.startswith('poetry_part_') and f.endswith('.json')]

            if not part_files:
                return False

            for filename in sorted(part_files):
                filepath = os.path.join(self.parts_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.poetry_data.extend(data)
                except Exception as e:
                    logging.warning(f"加载分片 {filename} 失败: {e}")

            if self.poetry_data:
                self.is_loaded = True
                logging.info(f"从分片文件加载了 {len(self.poetry_data)} 首诗词")
                return True

        except Exception as e:
            logging.error(f"分片文件加载失败: {e}")

        return False

    def _load_from_json(self):
        """从单个JSON文件加载"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.poetry_data = json.load(f)

            if self.poetry_data:
                self.is_loaded = True
                logging.info(f"从JSON文件加载了 {len(self.poetry_data)} 首诗词")
                return True

        except Exception as e:
            logging.error(f"JSON文件加载失败: {e}")

        return False

    def _load_from_sample(self):
        """从示例数据文件加载"""
        try:
            with open(self.sample_path, 'r', encoding='utf-8') as f:
                self.poetry_data = json.load(f)

            if self.poetry_data:
                self.is_loaded = True
                logging.info(f"从示例文件加载了 {len(self.poetry_data)} 首诗词")
                return True

        except Exception as e:
            logging.error(f"示例文件加载失败: {e}")

        return False

    def _load_from_clean(self):
        """从清洁数据文件加载"""
        try:
            with open(self.clean_path, 'r', encoding='utf-8') as f:
                self.poetry_data = json.load(f)

            if self.poetry_data:
                self.is_loaded = True
                logging.info(f"从清洁数据文件加载了 {len(self.poetry_data)} 首诗词")
                return True

        except Exception as e:
            logging.error(f"清洁数据文件加载失败: {e}")

        return False

    def ensure_loaded(self):
        """确保知识库加载完毕"""
        if not self.is_loaded:
            self._load_data()

        if not self.is_loaded:
            raise Exception("无法加载诗词知识库，请检查数据文件是否存在")

    def search(self, query: str, limit: int = 50):
        """
        搜索包含查询词的诗词
        :param query: 搜索词
        :param limit: 返回结果数量限制
        :return: 匹配的诗词列表
        """
        if not self.is_loaded:
            self.ensure_loaded()

        if not query.strip():
            return []

        results = []
        query = query.strip()

        for poem in self.poetry_data:
            if len(results) >= limit:
                break

            # 检查标题和内容
            title = poem.get('title', '')
            author = poem.get('author', '')
            content = poem.get('content', [])

            # 将content转换为字符串进行搜索
            if isinstance(content, list):
                content_str = ''.join(content)
            else:
                content_str = str(content)

            # 如果查询词在标题、作者或内容中出现
            if query in title or query in author or query in content_str:
                results.append(poem)

        return results

    # 常见繁简体和异体字映射（类级别，避免重复创建）
    _CHAR_MAP = {
        '\u5acc': '\u601c',  # 嫌(U+5ACC) -> 怜(U+601C) - 数据库错误：游园不值中应该是"怜"但存储成了"嫌"
    }

    def _normalize_text(self, text):
        """归一化文本：统一常见异体字/繁简体"""
        # 快速路径：如果没有需要替换的字符，直接返回
        if not any(c in self._CHAR_MAP for c in text):
            return text

        # 只在需要时才进行替换
        return ''.join(self._CHAR_MAP.get(c, c) for c in text)

    def _build_index(self):
        """构建字符倒排索引（后台异步执行）"""
        if self._index_built or not self.is_loaded:
            return

        import re
        from collections import defaultdict

        logging.info("开始构建诗词索引...")
        start_time = logging.time if hasattr(logging, 'time') else None

        # 使用defaultdict简化代码
        char_index = defaultdict(list)
        split_pattern = re.compile(r'[，。？！,?!；;]')

        for poem_idx, poem in enumerate(self.poetry_data):
            content = poem.get('content', [])
            if isinstance(content, str):
                content = [content]

            for line in content:
                clauses = split_pattern.split(line)

                for clause in clauses:
                    clause = clause.strip()

                    # 只索引5字或7字诗句
                    if len(clause) not in [5, 7]:
                        continue

                    # 归一化诗句
                    normalized_clause = self._normalize_text(clause)

                    # 为诗句中的每个字符建立索引
                    for char in set(normalized_clause):
                        char_index[char].append((poem_idx, clause, normalized_clause))

        self._char_index = dict(char_index)
        self._index_built = True

        logging.info(f"索引构建完成，索引了 {len(self._char_index)} 个字符")

    def ensure_index(self):
        """确保索引已构建"""
        if not self._index_built:
            self._build_index()

    def find_poem_from_chars(self, chars):
        """
        从给定字符中查找可以组成的诗句
        :param chars: 可用字符
        :return: [(poem_dict, matched_clauses), ...] 或 None
        """
        if not self.is_loaded:
            self.ensure_loaded()

        clean_chars = chars.strip()
        if not clean_chars:
            return None

        # 归一化输入字符
        clean_chars = self._normalize_text(clean_chars)

        normalized_key = ''.join(sorted(clean_chars))
        if normalized_key in self._poem_cache:
            return self._poem_cache[normalized_key]

        # 确保索引已构建
        self.ensure_index()

        from collections import Counter

        chars_counter = Counter(clean_chars)
        chars_set = set(clean_chars)

        # 使用索引快速查找候选诗句
        # 策略：找出题目中最少见的字符，从它的索引开始
        candidate_clauses = set()

        # 找到索引最小的字符（最不常见）
        min_char = None
        min_count = float('inf')

        for char in chars_set:
            if char in self._char_index:
                count = len(self._char_index[char])
                if count < min_count:
                    min_count = count
                    min_char = char

        if min_char is None:
            # 没有任何字符在索引中
            outcome = None
        else:
            # 从最少见的字符开始，获取候选诗句
            for poem_idx, clause, normalized_clause in self._char_index[min_char]:
                # 快速检查：诗句的所有字符都在题目中
                if all(c in chars_set for c in normalized_clause):
                    # 精确检查字符数量
                    clause_counter = Counter(normalized_clause)
                    if all(clause_counter[c] <= chars_counter[c] for c in clause_counter):
                        candidate_clauses.add((poem_idx, clause))

            # 组织结果：按诗词分组
            results_dict = {}
            for poem_idx, clause in candidate_clauses:
                if poem_idx not in results_dict:
                    results_dict[poem_idx] = []
                results_dict[poem_idx].append(clause)

            # 转换为原格式
            results = []
            for poem_idx, clauses in sorted(results_dict.items())[:10]:
                poem = self.poetry_data[poem_idx]
                results.append((poem, clauses))

            outcome = results[:5] if results else None

        # 缓存结果
        if len(self._poem_cache) >= 32:
            try:
                self._poem_cache.pop(next(iter(self._poem_cache)))
            except StopIteration:
                pass
        self._poem_cache[normalized_key] = outcome
        return outcome

    def _resolve_path(self, path):
        """将传入路径解析为绝对路径，保留外部传入的绝对路径"""
        if not path:
            return None
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(self.base_dir, path))

    def release(self):
        """释放内存占用，便于应用退出时清理资源"""
        self.poetry_data.clear()
        self.is_loaded = False
        self._poem_cache.clear()
        self._char_index.clear()
        self._index_built = False

# 测试代码
if __name__ == '__main__':
    try:
        kb = KnowledgeBaseManager()
        print(f"知识库加载状态: {kb.is_loaded}")
        print(f"诗词数量: {len(kb.poetry_data) if kb.poetry_data else 0}")

        # 测试搜索
        results = kb.search("明月")
        print(f"搜索'明月'结果: {len(results)}首")

    except Exception as e:
        print(f"测试失败: {e}")
