import json
import base64
import logging
from io import BytesIO
from types import SimpleNamespace

import httpx

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
        self.vision_models = [
            "gpt-4-vision-preview", "gpt-4v", "gpt-4-v", "gpt-4o",
            "glm-4v",
            "qwen-vl-plus", "qwen-vl-max",
            "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
        ]
        
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
        model = config.get("model")

        if image and model in self.vision_models:
            return self._get_openai_compatible_answer(config, question_text, image)
        else:
            return self._get_openai_compatible_answer(config, question_text)

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

        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        if image and model in self.vision_models:
            try:
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

        logging.info(f"Sending to AI with {len(messages)} message(s)")

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": float(config.get("temperature", 0.7)),
            "max_tokens": min(int(config.get("max_tokens", 1000)), 4000),
        }

        extra_args = {}
        if isinstance(config, dict):
            for key in ("top_p", "presence_penalty", "frequency_penalty", "stop"):
                if key in config:
                    extra_args[key] = config[key]
        if extra_args:
            payload.update(extra_args)

        try:
            return self._stream_chat_completion(base_url, api_key, payload, config)
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise Exception(f"OpenAI API错误: {str(e)}")

    def _stream_chat_completion(self, base_url, api_key, payload, config):
        """直接使用httpx与OpenAI兼容接口进行流式对话请求"""
        timeout = float(config.get("timeout", 60)) if isinstance(config, dict) else 60

        proxies = None
        if isinstance(config, dict):
            proxies = config.get("proxies")
        proxies = self._normalize_proxies(proxies)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        url = base_url.rstrip("/") + "/chat/completions"

        client_kwargs = {"timeout": timeout}
        if proxies:
            client_kwargs["proxies"] = proxies

        try:
            client = httpx.Client(**client_kwargs)
        except Exception as e:
            raise ValueError(f"创建HTTP客户端失败: {e}")

        def _iter_stream():
            try:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            line = line[6:]
                        line = line.strip()
                        if not line:
                            continue
                        if line == "[DONE]":
                            break
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            logging.warning(f"无法解析的流式返回: {line}")
                            continue
                        delta = ""
                        choices = event.get("choices", [])
                        if choices:
                            choice = choices[0]
                            delta = choice.get("delta", {}).get("content") or choice.get("text", "")
                        yield SimpleNamespace(
                            choices=[SimpleNamespace(delta=SimpleNamespace(content=delta or ""))]
                        )
            except httpx.HTTPStatusError as e:
                detail = e.response.text
                raise ValueError(f"API调用失败: {detail}")
            except httpx.HTTPError as e:
                raise ValueError(f"网络请求失败: {e}")
            finally:
                client.close()

        return _iter_stream()

    def _normalize_proxies(self, proxies):
        if not proxies:
            return None
        if isinstance(proxies, str):
            return {
                "http": proxies,
                "https": proxies,
            }
        if isinstance(proxies, dict):
            normalized = {}
            # 支持常见键名
            http_proxy = proxies.get("http") or proxies.get("http://") or proxies.get("HTTP")
            https_proxy = proxies.get("https") or proxies.get("https://") or proxies.get("HTTPS")
            all_proxy = proxies.get("all") or proxies.get("ALL") or proxies.get("all://")
            if all_proxy:
                normalized["http"] = all_proxy
                normalized["https"] = all_proxy
            if http_proxy:
                normalized["http"] = http_proxy
            if https_proxy:
                normalized["https"] = https_proxy
            return normalized or None
        return None
