import google.generativeai as genai
import os
import json
from typing import List, Dict, Optional
from PIL import Image
import io

class AIService:
    """Service for AI integration with Gemini"""
    
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None
    
    def generate_post_description(self, image_path: str, language: str = 'ru') -> Optional[str]:
        """Generate description for a post based on image"""
        if not self.is_available():
            return None
        
        try:
            # Load and process image
            image = Image.open(image_path)
            
            # Resize image if too large
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Generate description
            prompt = self._get_description_prompt(language)
            response = self.model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_byte_arr}])
            
            return response.text.strip()
        except Exception as e:
            print(f"Error generating description: {e}")
            return None
    
    def generate_hashtags(self, description: str, language: str = 'ru') -> List[str]:
        """Generate hashtags based on description"""
        if not self.is_available() or not description:
            return []
        
        try:
            prompt = self._get_hashtag_prompt(description, language)
            response = self.model.generate_content(prompt)
            
            # Parse hashtags from response
            hashtags = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line.startswith('#'):
                    hashtag = line[1:].strip()
                    if hashtag and len(hashtag) <= 50:  # Instagram hashtag limit
                        hashtags.append(hashtag)
            
            return hashtags[:10]  # Limit to 10 hashtags
        except Exception as e:
            print(f"Error generating hashtags: {e}")
            return []
    
    def enhance_post_content(self, content: str, language: str = 'ru') -> Optional[str]:
        """Enhance post content with AI"""
        if not self.is_available() or not content:
            return None
        
        try:
            prompt = self._get_enhancement_prompt(content, language)
            response = self.model.generate_content(prompt)
            
            return response.text.strip()
        except Exception as e:
            print(f"Error enhancing content: {e}")
            return None
    
    def _get_description_prompt(self, language: str) -> str:
        """Get prompt for image description generation"""
        prompts = {
            'ru': """
            Проанализируй это изображение и создай краткое, привлекательное описание для поста в социальной сети.
            Описание должно быть:
            - Интересным и привлекательным
            - Длиной 1-2 предложения
            - Подходящим для Instagram-стиля
            - На русском языке
            - Без эмодзи
            """,
            'en': """
            Analyze this image and create a brief, engaging description for a social media post.
            The description should be:
            - Interesting and engaging
            - 1-2 sentences long
            - Suitable for Instagram style
            - In English
            - Without emojis
            """,
            'kk': """
            Бұл суретті талдап, әлеуметтік желідегі жазба үшін қысқа, тартымды сипаттама жасаңыз.
            Сипаттама мынадай болуы керек:
            - Қызықты және тартымды
            - 1-2 сөйлем ұзындығында
            - Instagram стиліне сәйкес
            - Қазақ тілінде
            - Эмодзисыз
            """
        }
        return prompts.get(language, prompts['ru'])
    
    def _get_hashtag_prompt(self, description: str, language: str) -> str:
        """Get prompt for hashtag generation"""
        prompts = {
            'ru': f"""
            На основе этого описания поста создай 5-10 релевантных хэштегов:
            "{description}"
            
            Хэштеги должны быть:
            - Релевантными содержанию
            - Популярными в социальных сетях
            - Без пробелов и специальных символов
            - Начинаться с #
            - На русском или английском языке
            """,
            'en': f"""
            Based on this post description, create 5-10 relevant hashtags:
            "{description}"
            
            Hashtags should be:
            - Relevant to the content
            - Popular on social media
            - Without spaces and special characters
            - Starting with #
            - In English
            """,
            'kk': f"""
            Бұл жазба сипаттамасына негіздеп, 5-10 тиісті хэштег жасаңыз:
            "{description}"
            
            Хэштегтер мынадай болуы керек:
            - Мазмұнға тиісті
            - Әлеуметтік желілерде танымал
            - Бос орындар мен арнайы таңбаларсыз
            - # таңбасынан басталуы керек
            - Қазақ немесе ағылшын тілінде
            """
        }
        return prompts.get(language, prompts['ru'])
    
    def _get_enhancement_prompt(self, content: str, language: str) -> str:
        """Get prompt for content enhancement"""
        prompts = {
            'ru': f"""
            Улучши этот текст поста, сделав его более привлекательным и интересным:
            "{content}"
            
            Улучшенный текст должен:
            - Сохранить основную идею
            - Быть более привлекательным
            - Иметь лучшую структуру
            - Быть подходящим для социальных сетей
            - Оставаться на русском языке
            """,
            'en': f"""
            Enhance this post text to make it more attractive and interesting:
            "{content}"
            
            The enhanced text should:
            - Keep the main idea
            - Be more attractive
            - Have better structure
            - Be suitable for social media
            - Remain in English
            """,
            'kk': f"""
            Бұл жазба мәтінін жақсартып, оны тартымдырақ және қызықтырақ етіңіз:
            "{content}"
            
            Жақсартылған мәтін мынадай болуы керек:
            - Негізгі идеяны сақтау
            - Тартымдырақ болу
            - Жақсырақ құрылымға ие болу
            - Әлеуметтік желілерге сәйкес болу
            - Қазақ тілінде қалу
            """
        }
        return prompts.get(language, prompts['ru'])

# Global instance
ai_service = AIService()






