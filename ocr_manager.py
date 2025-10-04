import pytesseract
from PIL import Image
import os
import requests
import base64
import json
from io import BytesIO
import time
import logging

class OCRManager:
    def __init__(self):
        self.settings = {
            "type": "tesseract", #可以是 "tesseract", "baidu"
            "tesseract_path": "",
            "language": "chi_sim+eng",
            "baidu_api_key": "",
            "baidu_secret_key": ""
        }
        self.load_settings({})
        self.baidu_access_token = None
        self.baidu_token_expire_time = 0
        self.preload_ocr_engine()
        
    def load_settings(self, settings):
        """加载OCR设置"""
        self.settings.update(settings)
        self._configure_tesseract()
        
    def get_settings(self):
        """获取OCR设置"""
        return self.settings
        
    def _configure_tesseract(self):
        """配置Tesseract-OCR路径"""
        tesseract_path = self.settings.get("tesseract_path")
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            pass
            
    def extract_text(self, image: Image.Image) -> str:
        """
        从图片中提取文字
        :param image: PIL Image对象
        :return: 提取到的文本
        """
        ocr_type = self.settings.get("type", "tesseract")
        
        if ocr_type == "tesseract":
            return self._extract_text_tesseract(image)
        elif ocr_type == "baidu":
            return self._extract_text_baidu(image)
        else:
            raise ValueError(f"不支持的OCR类型: {ocr_type}")
            
    def preload_ocr_engine(self):
        ocr_type = self.settings.get("type")
        if ocr_type == "tesseract":
            try:
                pytesseract.image_to_string(Image.new('RGB', (1, 1)), lang=self.settings.get("language"))
            except Exception:
                pass
    
    def _extract_text_tesseract(self, image: Image.Image) -> str:
        """
        使用Tesseract从图片中提取文字
        """
        if not pytesseract.pytesseract.tesseract_cmd:
            raise ValueError("Tesseract-OCR路径未配置，请在设置中配置。")
            
        try:
            start_time = time.time()
            text = pytesseract.image_to_string(image, lang=self.settings.get("language"))
            end_time = time.time()
            logging.info(f"Tesseract OCR took {end_time - start_time:.2f} seconds")
            return text
        except pytesseract.TesseractNotFoundError:
            raise Exception("Tesseract-OCR未找到，请检查路径配置。")
        except Exception as e:
            raise Exception(f"Tesseract OCR识别失败: {str(e)}")
            
    def _get_baidu_access_token(self, retries=3, delay=1):
        """
        获取百度云OCR的Access Token，带重试逻辑
        """
        if self.baidu_access_token and self.baidu_token_expire_time > time.time():
            return self.baidu_access_token
            
        api_key = self.settings.get("baidu_api_key")
        secret_key = self.settings.get("baidu_secret_key")
        
        if not api_key or not secret_key:
            raise ValueError("百度云OCR API Key或Secret Key未配置")
            
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        
        for i in range(retries):
            try:
                response = requests.post(url, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                if "access_token" in result:
                    self.baidu_access_token = result["access_token"]
                    self.baidu_token_expire_time = time.time() + result.get("expires_in", 0) - 300 # 提前5分钟过期
                    return self.baidu_access_token
                else:
                    raise Exception(f"获取百度云Access Token失败: {result.get('error_description', result)}")
            except requests.exceptions.RequestException as e:
                if i < retries - 1:
                    time.sleep(delay)
                else:
                    raise Exception(f"请求百度云Access Token失败: {str(e)}")
            
    def _extract_text_baidu(self, image: Image.Image) -> str:
        """
        使用百度云OCR从图片中提取文字
        """
        start_time = time.time()
        access_token = self._get_baidu_access_token()
        
        # 将PIL Image转换为base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # 百度云通用文字识别接口
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "image": img_base64
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "words_result" in result:
                text_lines = [item["words"] for item in result["words_result"]]
                end_time = time.time()
                logging.info(f"Baidu OCR took {end_time - start_time:.2f} seconds")
                return "\n".join(text_lines)
            elif "error_code" in result:
                raise Exception(f"百度云OCR识别错误: {result.get('error_msg', '未知错误')} (错误码: {result.get('error_code')})")
            else:
                return "" # 没有识别到文字
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求百度云OCR识别失败: {str(e)}")
        except Exception as e:
            raise Exception(f"百度云OCR识别失败: {str(e)}")
