from openai import OpenAI
import json
import base64
import logging
from io import BytesIO
from PIL import Image

class AIManager:
    DEFAULT_PROMPT = """你是一个专业的问题回答助手。请根据用户提供的题目，给出准确、详细的答案。

要求：
1. 回答要简重点突出
2. 如果是选择题，请明确指出正确答案
3. 如果是计算题，请提供详细的解题步骤
4. 如果是概念题，请给出准确的定义和解释
5. 回答要有逻辑性，条理清晰

请直接回答问题，不需要额外的寒暄。"""

    def __init__(self):
        # AI配置字典，格式：{name: config_dict}
        self.ai_configs = {}
        self.system_prompt = self.DEFAULT_PROMPT
        
    def load_settings(self, settings):
        """
        加载AI设置
        :param settings: 包含AI配置的字典
        """
        if not isinstance(settings, dict):
            raise ValueError("设置必须是字典格式")
            
        if "configs" in settings:
            if not isinstance(settings["configs"], dict):
                raise ValueError("AI配置必须是字典格式")
            self.ai_configs = settings["configs"]
            
        if "system_prompt" in settings:
            if not isinstance(settings["system_prompt"], str):
                raise ValueError("系统提示词必须是字符串")
            self.system_prompt = settings["system_prompt"]
        
    def get_settings(self):
        """
        获取AI设置
        :return: 包含所有设置的字典
        """
        return {
            "configs": self.ai_configs.copy(),
            "system_prompt": self.system_prompt
        }
        
    def add_ai_config(self, name, config):
        """
        添加或更新AI配置
        :param name: AI配置名称
        :param config: AI配置字典
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("AI名称不能为空")
            
        if not isinstance(config, dict):
            raise ValueError("AI配置必须是字典格式")
            
        required_fields = ["type", "api_key"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"AI配置缺少必要字段: {field}")
                
        self.ai_configs[name.strip()] = config.copy()
        
    def remove_ai_config(self, name):
        """
        删除AI配置
        :param name: 要删除的AI配置名称
        :return: 是否删除成功
        """
        if name in self.ai_configs:
            del self.ai_configs[name]
            return True
        return False
        
    def get_ai_config(self, name):
        """
        获取指定的AI配置
        :param name: AI配置名称
        :return: AI配置字典的副本，如果不存在返回None
        """
        config = self.ai_configs.get(name)
        return config.copy() if config else None
            
    def get_enabled_ais(self):
        """获取启用的AI配置"""
        return {name: config for name, config in self.ai_configs.items() 
                if config.get("enabled", False)}
                
    def get_answer(self, ai_name, config, question_text, image=None):
        """
        获取AI回答（调度器）
        :param ai_name: AI名称
        :param config: AI配置
        :param question_text: 题目文本
        :param image: 题目图片（可选）
        :return: AI回答
        """
        ai_type = config.get("type", "openai").lower()

        # 对于兼容OpenAI的API，统一处理
        # 支持 "openai", "doubao", "siliconflow" 等
        if ai_type in ["openai", "doubao", "siliconflow", "custom"]:
            return self._get_openai_compatible_answer(config, question_text, image)
        # 在这里可以为其他AI类型（如claude, gemini）添加分支
        # elif ai_type == "claude":
        #     return self._get_claude_answer(config, question_text, image)
        else:
            # 默认使用OpenAI兼容模式，以支持用户自定义类型
            return self._get_openai_compatible_answer(config, question_text, image)

    def _get_openai_compatible_answer(self, config, question_text, image=None):
        """获取与OpenAI API兼容的服务的回答"""
        api_key = config.get("api_key")
        base_url = config.get("base_url", "").strip()
        model = config.get("model")

        if not api_key:
            raise ValueError("API密钥未配置")
        if not model:
            raise ValueError("模型未配置")

        # 如果是官方openai且未指定base_url，则使用默认值
        if config.get("type") == "openai" and not base_url:
            base_url = "https://api.openai.com/v1"

        try:
            # 初始化OpenAI客户端
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
            ]

            # 定义支持视觉的模型列表
            vision_models = [
                "gpt-4-vision-preview", "gpt-4v", "gpt-4-v", "gpt-4o",
                "glm-4v",  # 智谱
                "qwen-vl-plus", "qwen-vl-max", # 通义千问
                "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", # Claude 3也支持
            ]

            # 如果有图片且模型支持视觉
            if image and model in vision_models:
                try:
                    # 将图片转换为base64
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"请回答图片中的题目。如果图片中有文字题目，请优先使用图片内容。识别到的文字内容：{question_text}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    })
                except Exception as e:
                    raise Exception(f"图片处理失败: {str(e)}")
            else:
                messages.append({
                    "role": "user",
                    "content": question_text
                })
                
            # 发送请求
            try:
                # 调整API参数
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=min(int(config.get("max_tokens", 1000)), 4000),
                    temperature=float(config.get("temperature", 0.7))
                )
                
                # 确保响应有效
                if not completion or not hasattr(completion, 'choices') or not completion.choices:
                    raise ValueError("无效的API响应格式")
                
                # 获取第一个选择
                first_choice = completion.choices[0]
                if not first_choice or not hasattr(first_choice, 'message'):
                    raise ValueError("无效的API响应消息格式")
                
                # 获取消息内容
                message = first_choice.message
                if not message or not hasattr(message, 'content'):
                    raise ValueError("无效的消息内容格式")
                
                # 尝试从多个可能的属性获取回答内容
                answer = getattr(message, 'content', None)
                
                # 如果 content 为空，尝试从 text 属性获取
                if not answer:
                    answer = getattr(message, 'text', None)

                # 如果还是空，尝试从 annotations 获取
                if not answer:
                    annotations = getattr(message, 'annotations', None)
                    if annotations and isinstance(annotations, list) and len(annotations) > 0:
                        # 简单地将所有 annotation 连接起来
                        answer = " ".join(str(a) for a in annotations)

                # 如果仍然没有找到回答，则记录日志并抛出错误
                if not answer:
                    logging.error(f"无法提取回答。完整的API响应: {completion}")
                    raise ValueError("API返回的回答内容为空或格式不兼容")
                    
                return answer
                
            except (AttributeError, IndexError) as e:
                raise ValueError(f"API响应格式错误: {str(e)}")
                
            except Exception as e:
                raise ValueError(f"API调用失败: {str(e)}")
            
        except Exception as e:
            raise Exception(f"OpenAI API错误: {str(e)}")
