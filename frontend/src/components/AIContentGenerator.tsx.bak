import React, { useState } from 'react';
import apiService from '../services/api';

interface AIContentGeneratorProps {
  onContentGenerated: (content: string, hashtags: string[]) => void;
  language?: 'ru' | 'en' | 'kk';
}

export const AIContentGenerator: React.FC<AIContentGeneratorProps> = ({
  onContentGenerated,
  language = 'ru'
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState(language);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const generateContent = async () => {
    if (!selectedFile) return;

    setIsGenerating(true);
    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('language', selectedLanguage);

      const response = await apiService.post('/ai/auto-generate-post', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { description, hashtags } = response.data;
      onContentGenerated(description || '', hashtags || []);
    } catch (error) {
      console.error('Error generating content:', error);
      alert('Ошибка при генерации контента');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateHashtags = async (description: string) => {
    if (!description.trim()) return;

    setIsGenerating(true);
    try {
      const response = await apiService.post('/ai/generate-hashtags', {
        description,
        language: selectedLanguage
      });

      const { hashtags } = response.data;
      return hashtags || [];
    } catch (error) {
      console.error('Error generating hashtags:', error);
      return [];
    } finally {
      setIsGenerating(false);
    }
  };

  const enhanceContent = async (content: string) => {
    if (!content.trim()) return;

    setIsGenerating(true);
    try {
      const response = await apiService.post('/ai/enhance-content', {
        content,
        language: selectedLanguage
      });

      const { enhanced_content } = response.data;
      return enhanced_content || content;
    } catch (error) {
      console.error('Error enhancing content:', error);
      return content;
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <h3 className="text-lg font-semibold mb-4">🤖 AI Генератор контента</h3>
      
      {/* Language Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Язык генерации:
        </label>
        <select
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value as 'ru' | 'en' | 'kk')}
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="ru">Русский</option>
          <option value="en">English</option>
          <option value="kk">Қазақша</option>
        </select>
      </div>

      {/* File Upload */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Загрузите изображение для анализа:
        </label>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Image Preview */}
      {preview && (
        <div className="mb-4">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-48 object-cover rounded-md"
          />
        </div>
      )}

      {/* Generate Button */}
      <button
        onClick={generateContent}
        disabled={!selectedFile || isGenerating}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {isGenerating ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Генерирую...
          </>
        ) : (
          '🎨 Сгенерировать описание и хэштеги'
        )}
      </button>

      {/* AI Features Info */}
      <div className="mt-4 p-3 bg-blue-50 rounded-md">
        <h4 className="text-sm font-medium text-blue-800 mb-2">Возможности AI:</h4>
        <ul className="text-xs text-blue-700 space-y-1">
          <li>• Автоматическое описание изображений</li>
          <li>• Генерация релевантных хэштегов</li>
          <li>• Улучшение текста постов</li>
          <li>• Поддержка 3 языков</li>
        </ul>
      </div>
    </div>
  );
};
