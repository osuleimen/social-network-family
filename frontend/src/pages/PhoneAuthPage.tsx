import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import apiClient from '../services/api';
import { Phone, MessageSquare, RotateCcw, CheckCircle, Moon, Sun } from 'lucide-react';

// Phone number validation schema
const phoneSchema = z.object({
  phone_number: z.string()
    .min(1, 'Номер телефона обязателен')
    .transform((val) => val.replace(/\D/g, '')) // Убираем все не-цифры для валидации
    .refine((val) => /^7[0-9]{10}$/.test(val), {
      message: 'Введите корректный казахстанский номер телефона'
    })
});

// Verification code schema
const codeSchema = z.object({
  verification_code: z.string()
    .min(4, 'Код должен содержать 4 цифры')
    .max(4, 'Код должен содержать 4 цифры')
    .regex(/^[0-9]+$/, 'Код должен содержать только цифры')
});

type PhoneFormData = z.infer<typeof phoneSchema>;
type CodeFormData = z.infer<typeof codeSchema>;

type AuthStep = 'phone' | 'verification';

const PhoneAuthPage = () => {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [step, setStep] = useState<AuthStep>('phone');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isNewUser, setIsNewUser] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [error, setError] = useState('');
  const [isWaitingForExistingCode, setIsWaitingForExistingCode] = useState(false);

  // Phone form
  const phoneForm = useForm<PhoneFormData>({
    resolver: zodResolver(phoneSchema),
  });

  // Code form
  const codeForm = useForm<CodeFormData>({
    resolver: zodResolver(codeSchema),
  });

  // Request SMS code mutation
  const requestCodeMutation = useMutation({
    mutationFn: (data: PhoneFormData) => apiClient.requestSMSCode(data.phone_number),
    onSuccess: (data) => {
      setPhoneNumber(data.phone_number);
      setIsNewUser(data.is_new_user);
      setStep('verification');
      setError('');
      
      if (data.is_new_user) {
        // Новый пользователь - отправляем SMS и показываем countdown
        setIsWaitingForExistingCode(false);
        startCountdown();
      } else if (data.has_existing_code) {
        // Существующий пользователь с действующим кодом - ждем ввода существующего кода
        setIsWaitingForExistingCode(true);
        // НЕ запускаем countdown, ждем ввода старого кода
      } else {
        // Существующий пользователь без действующего кода - был отправлен новый SMS
        setIsWaitingForExistingCode(false);
        startCountdown();
      }
      
      codeForm.reset();
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Ошибка отправки SMS');
    },
  });

  // Verify code mutation
  const verifyCodeMutation = useMutation({
    mutationFn: (data: CodeFormData) => 
      apiClient.verifySMSCode(phoneNumber, data.verification_code),
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      setUser(data.user);
      navigate('/');
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.error || 'Неверный код подтверждения';
      setError(errorMessage);
      
      // Если код неверный и это существующий пользователь, предлагаем отправить новый
      if (errorMessage.includes('Invalid verification code') && !isNewUser) {
        setIsWaitingForExistingCode(false);
        startCountdown();
      }
    },
  });

  // Resend code mutation
  const resendCodeMutation = useMutation({
    mutationFn: () => apiClient.resendSMSCode(phoneNumber),
    onSuccess: () => {
      setError('');
      setIsWaitingForExistingCode(false);
      startCountdown();
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Ошибка отправки SMS');
    },
  });

  const startCountdown = () => {
    setCountdown(60);
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handlePhoneSubmit = (data: PhoneFormData) => {
    setError('');
    // Преобразуем отформатированный номер в формат для API (+7XXXXXXXXXX)
    const cleanDigits = data.phone_number.replace(/\D/g, '');
    const formattedForAPI = '+' + cleanDigits;
    requestCodeMutation.mutate({ phone_number: formattedForAPI });
  };

  const handleCodeSubmit = (data: CodeFormData) => {
    setError('');
    verifyCodeMutation.mutate(data);
  };

  const handleResendCode = () => {
    setError('');
    resendCodeMutation.mutate();
  };

  const handleBackToPhone = () => {
    setStep('phone');
    setPhoneNumber('');
    setError('');
    setIsWaitingForExistingCode(false);
    phoneForm.reset();
    codeForm.reset();
  };

  const formatPhoneNumber = (value: string) => {
    // Remove all non-digit characters
    let digits = value.replace(/\D/g, '');
    
    // Handle different input scenarios
    if (digits.startsWith('8')) {
      // Replace 8 with 7 (Russian format)
      digits = '7' + digits.slice(1);
    } else if (!digits.startsWith('7') && digits.length > 0) {
      // Add 7 prefix if missing
      digits = '7' + digits;
    }
    
    // Ensure we don't exceed 11 digits (7 + 10 digits)
    if (digits.length > 11) {
      digits = digits.slice(0, 11);
    }
    
    // Format as +7 XXX XXX XX XX (like WhatsApp/Telegram)
    if (digits.length === 0) return '';
    if (digits.length === 1) return '+7';
    if (digits.length <= 4) return `+7 ${digits.slice(1)}`;
    if (digits.length <= 7) return `+7 ${digits.slice(1, 4)} ${digits.slice(4)}`;
    if (digits.length <= 9) return `+7 ${digits.slice(1, 4)} ${digits.slice(4, 7)} ${digits.slice(7)}`;
    return `+7 ${digits.slice(1, 4)} ${digits.slice(4, 7)} ${digits.slice(7, 9)} ${digits.slice(9, 11)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      {/* Theme toggle */}
      <button
        onClick={toggleDarkMode}
        className="absolute top-4 right-4 p-2 rounded-lg bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-all"
      >
        {isDarkMode ? <Sun className="h-5 w-5 text-yellow-500" /> : <Moon className="h-5 w-5 text-gray-600" />}
      </button>

      <div className="max-w-md w-full">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mb-4">
              {step === 'phone' ? (
                <Phone className="h-8 w-8 text-white" />
              ) : (
                <MessageSquare className="h-8 w-8 text-white" />
              )}
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {step === 'phone' ? 'Вход в аккаунт' : 'Подтверждение'}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {step === 'phone' 
                ? 'Введите номер телефона для входа или регистрации'
                : `Введите код из SMS, отправленного на ${phoneNumber}`
              }
            </p>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Phone number step */}
          {step === 'phone' && (
            <form onSubmit={phoneForm.handleSubmit(handlePhoneSubmit)} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Номер телефона
                </label>
                <div className="relative">
                  <input
                    {...phoneForm.register('phone_number')}
                    type="tel"
                    placeholder="+7 777 777 77 77"
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                    onChange={(e) => {
                      const formatted = formatPhoneNumber(e.target.value);
                      phoneForm.setValue('phone_number', formatted);
                    }}
                    onPaste={(e) => {
                      e.preventDefault();
                      const pastedText = e.clipboardData.getData('text');
                      const formatted = formatPhoneNumber(pastedText);
                      phoneForm.setValue('phone_number', formatted);
                    }}
                  />
                  <Phone className="absolute right-3 top-3 h-5 w-5 text-gray-400" />
                </div>
                {phoneForm.formState.errors.phone_number && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {phoneForm.formState.errors.phone_number.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={requestCodeMutation.isLoading}
                className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-blue-600 hover:to-indigo-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {requestCodeMutation.isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Отправка SMS...
                  </div>
                ) : (
                  'Войти'
                )}
              </button>
            </form>
          )}

          {/* Verification step */}
          {step === 'verification' && (
            <div className="space-y-6">
              {/* User status indicator */}
              <div className="bg-blue-50 dark:bg-blue-900/50 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-2" />
                  <p className="text-blue-800 dark:text-blue-200 text-sm">
                    {isNewUser 
                      ? 'Новый пользователь - создадим аккаунт' 
                      : isWaitingForExistingCode 
                        ? 'Введите код из предыдущего SMS' 
                        : 'Вход в существующий аккаунт'
                    }
                  </p>
                </div>
              </div>

              <form onSubmit={codeForm.handleSubmit(handleCodeSubmit)} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Код подтверждения
                  </label>
                  <input
                    {...codeForm.register('verification_code')}
                    type="text"
                    placeholder="0000"
                    maxLength={4}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-center text-2xl font-mono tracking-widest transition-all"
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '').slice(0, 4);
                      codeForm.setValue('verification_code', value);
                    }}
                  />
                  {codeForm.formState.errors.verification_code && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                      {codeForm.formState.errors.verification_code.message}
                    </p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={verifyCodeMutation.isLoading}
                  className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-600 hover:to-emerald-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {verifyCodeMutation.isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Проверка...
                    </div>
                  ) : (
                    'Подтвердить'
                  )}
                </button>
              </form>

              {/* Error message and request new code button */}
              {error && (
                <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <p className="text-red-800 dark:text-red-200 text-sm mb-3">{error}</p>
                  {error.includes('Invalid verification code') && !isNewUser && (
                    <button
                      onClick={handleResendCode}
                      disabled={resendCodeMutation.isLoading}
                      className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {resendCodeMutation.isLoading ? 'Отправка...' : 'Запросить новый код'}
                    </button>
                  )}
                </div>
              )}

              {/* Resend code section */}
              <div className="text-center">
                {isWaitingForExistingCode ? (
                  // Для случая ожидания существующего кода
                  <div className="space-y-3">
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      Если вы забыли код или он не приходит:
                    </p>
                    <button
                      onClick={handleResendCode}
                      disabled={resendCodeMutation.isLoading}
                      className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto transition-colors"
                    >
                      <RotateCcw className="h-4 w-4 mr-1" />
                      {resendCodeMutation.isLoading ? 'Отправка...' : 'Запросить новый код'}
                    </button>
                  </div>
                ) : (
                  // Для нового кода с countdown
                  countdown > 0 ? (
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                      Повторная отправка через {countdown} сек
                    </p>
                  ) : (
                    <button
                      onClick={handleResendCode}
                      disabled={resendCodeMutation.isLoading}
                      className="text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto transition-colors"
                    >
                      <RotateCcw className="h-4 w-4 mr-1" />
                      {resendCodeMutation.isLoading ? 'Отправка...' : 'Отправить код повторно'}
                    </button>
                  )
                )}
              </div>

              {/* Back to phone */}
              <div className="text-center">
                <button
                  onClick={handleBackToPhone}
                  className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-sm transition-colors"
                >
                  ← Изменить номер телефона
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            Нажимая "Войти", вы соглашаетесь с условиями использования
          </p>
        </div>
      </div>
    </div>
  );
};

export default PhoneAuthPage;

