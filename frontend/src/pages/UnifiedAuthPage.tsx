import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import apiClient from '../services/api';
import { Phone, Mail, MessageSquare, RotateCcw, CheckCircle, Moon, Sun, Eye, EyeOff } from 'lucide-react';

// Unified input validation schema
const unifiedInputSchema = z.object({
  input: z.string()
    .min(1, 'Введите номер телефона или email')
    .refine((val) => {
      // Check if it's an email
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (emailRegex.test(val)) {
        return true;
      }
      
      // Check if it's a phone number (only digits, 10-11 digits)
      const phoneDigits = val.replace(/\D/g, '');
      if (phoneDigits.length >= 10 && phoneDigits.length <= 11) {
        return true;
      }
      
      // Allow partial input for email (contains @ or letters)
      if (val.includes('@') || /[a-zA-Z]/.test(val)) {
        return true;
      }
      
      return false;
    }, {
      message: 'Введите корректный номер телефона или email'
    })
});

// Verification code schema
const codeSchema = z.object({
  verification_code: z.string()
    .min(6, 'Код должен содержать 6 цифр')
    .max(6, 'Код должен содержать 6 цифр')
    .regex(/^[0-9]+$/, 'Код должен содержать только цифры')
});

type UnifiedInputFormData = z.infer<typeof unifiedInputSchema>;
type CodeFormData = z.infer<typeof codeSchema>;

type AuthStep = 'input' | 'verification';
type AuthMethod = 'phone' | 'email' | 'google';

const UnifiedAuthPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { setUser } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [step, setStep] = useState<AuthStep>('input');
  const [inputValue, setInputValue] = useState('');
  const [authMethod, setAuthMethod] = useState<AuthMethod>('phone');
  const [isNewUser, setIsNewUser] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [error, setError] = useState('');
  const [isWaitingForExistingCode, setIsWaitingForExistingCode] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showManualCodeRequest, setShowManualCodeRequest] = useState(false);

  // Handle Google OAuth callback
  useEffect(() => {
    const success = searchParams.get('success');
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const isNewUserParam = searchParams.get('is_new_user');
    const authMethodParam = searchParams.get('auth_method');
    const errorParam = searchParams.get('error');
    const messageParam = searchParams.get('message');

    if (errorParam) {
      setError(`Ошибка авторизации: ${messageParam || errorParam}`);
      return;
    }

    if (success === 'true' && accessToken && refreshToken) {
      // Store tokens
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      
      // Set user data
      const userData = {
        id: 0, // Will be updated by AuthContext
        first_name: 'Google',
        last_name: 'User',
        email: '',
        username: '',
        is_verified: true,
        is_active: true,
        created_at: new Date().toISOString(),
        followers_count: 0,
        following_count: 0,
        posts_count: 0,
        auth_method: authMethodParam || 'google'
      };
      
      setUser(userData);
      setIsNewUser(isNewUserParam === 'true');
      
      // Navigate to main page
      navigate('/');
      
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [searchParams, setUser, navigate]);

  // Input form
  const inputForm = useForm<UnifiedInputFormData>({
    resolver: zodResolver(unifiedInputSchema),
  });

  // Code form
  const codeForm = useForm<CodeFormData>({
    resolver: zodResolver(codeSchema),
  });

  // Request verification code mutation
  const requestCodeMutation = useMutation({
    mutationFn: (data: UnifiedInputFormData) => {
      const input = data.input.trim();
      
      // Use unified API
      return apiClient.requestCode(input);
    },
    onSuccess: (data) => {
      setInputValue(data.identifier);
      setAuthMethod(data.type);
      setIsNewUser(data.is_new_user);
      setStep('verification');
      setError('');
      
      if (data.requires_manual_code_request) {
        // Registered user - show message to enter existing code or request new one
        setIsWaitingForExistingCode(true);
        setShowManualCodeRequest(true);
      } else if (data.is_new_user) {
        // New user
        setIsWaitingForExistingCode(false);
        setShowManualCodeRequest(false);
        startCountdown();
      } else if (data.has_existing_code) {
        // New user with existing code
        setIsWaitingForExistingCode(true);
        setShowManualCodeRequest(false);
      } else {
        // New user without existing code
        setIsWaitingForExistingCode(false);
        setShowManualCodeRequest(false);
        startCountdown();
      }
      
      codeForm.reset();
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Ошибка отправки кода');
    },
  });

  // Verify code mutation
  const verifyCodeMutation = useMutation({
    mutationFn: (data: CodeFormData) => {
      return apiClient.verifyCode(inputValue, data.verification_code);
    },
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
      
      if (errorMessage.includes('Invalid verification code') && !isNewUser) {
        setIsWaitingForExistingCode(false);
        startCountdown();
      }
    },
  });

  // Resend code mutation
  const resendCodeMutation = useMutation({
    mutationFn: () => {
      return apiClient.resendCode(inputValue);
    },
    onSuccess: () => {
      setError('');
      setIsWaitingForExistingCode(false);
      startCountdown();
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Ошибка отправки кода');
    },
  });

  // Force send code mutation (for registered users)
  const forceSendCodeMutation = useMutation({
    mutationFn: () => {
      return apiClient.forceSendCode(inputValue);
    },
    onSuccess: () => {
      setError('');
      setIsWaitingForExistingCode(false);
      setShowManualCodeRequest(false);
      startCountdown();
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Ошибка отправки кода');
    },
  });

  // Google OAuth mutation
  const googleAuthMutation = useMutation({
    mutationFn: () => apiClient.googleLogin(),
    onSuccess: (data) => {
      // Redirect to Google OAuth
      window.location.href = data.auth_url;
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Google OAuth временно недоступен. Используйте телефон или email для входа.');
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

  const handleInputSubmit = (data: UnifiedInputFormData) => {
    setError('');
    requestCodeMutation.mutate(data);
  };

  const handleCodeSubmit = (data: CodeFormData) => {
    setError('');
    verifyCodeMutation.mutate(data);
  };

  const handleResendCode = () => {
    setError('');
    resendCodeMutation.mutate();
  };

  const handleBackToInput = () => {
    setStep('input');
    setInputValue('');
    setError('');
    setIsWaitingForExistingCode(false);
    inputForm.reset();
    codeForm.reset();
  };

  const handleGoogleAuth = () => {
    setError('');
    googleAuthMutation.mutate();
  };

  const formatInput = (value: string) => {
    // Check if it looks like an email
    if (value.includes('@')) {
      return value;
    }
    
    // Format as phone number - only if user starts typing numbers
    let digits = value.replace(/\D/g, '');
    
    // Don't auto-add 7, let user type what they want
    if (digits.length > 11) {
      digits = digits.slice(0, 11);
    }
    
    if (digits.length === 0) return '';
    
    // Format with +7 prefix only if user typed 7 or 8
    if (digits.startsWith('7') || digits.startsWith('8')) {
      if (digits.startsWith('8') && digits.length === 11) {
        digits = '7' + digits.slice(1);
      }
      
      if (digits.length === 1) return '+7';
      if (digits.length <= 4) return `+7 ${digits.slice(1)}`;
      if (digits.length <= 7) return `+7 ${digits.slice(1, 4)} ${digits.slice(4)}`;
      if (digits.length <= 9) return `+7 ${digits.slice(1, 4)} ${digits.slice(4, 7)} ${digits.slice(7)}`;
      return `+7 ${digits.slice(1, 4)} ${digits.slice(4, 7)} ${digits.slice(7, 9)} ${digits.slice(9, 11)}`;
    }
    
    // For other cases, just return the digits as typed
    return digits;
  };

  const getInputIcon = () => {
    const input = inputForm.watch('input') || '';
    if (input.includes('@')) {
      return <Mail className="absolute right-3 top-3 h-5 w-5 text-gray-400" />;
    }
    return <Phone className="absolute right-3 top-3 h-5 w-5 text-gray-400" />;
  };

  const getInputPlaceholder = () => {
    const input = inputForm.watch('input') || '';
    if (input.includes('@')) {
      return 'example@email.com';
    }
    return '+7 777 777 77 77';
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
              {step === 'input' ? (
                <Phone className="h-8 w-8 text-white" />
              ) : (
                <MessageSquare className="h-8 w-8 text-white" />
              )}
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {step === 'input' ? 'Вход в аккаунт' : 'Подтверждение'}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {step === 'input' 
                ? 'Введите номер телефона или email для входа или регистрации'
                : `Введите код из ${authMethod === 'email' ? 'email' : 'SMS'}, отправленного на ${inputValue}`
              }
            </p>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Input step */}
          {step === 'input' && (
            <form onSubmit={inputForm.handleSubmit(handleInputSubmit)} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Номер телефона / email адрес
                </label>
                <div className="relative">
                  <input
                    {...inputForm.register('input')}
                    type="text"
                    placeholder={getInputPlaceholder()}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                    onChange={(e) => {
                      const value = e.target.value;
                      // Only format if it's not an email
                      if (value.includes('@') || /[a-zA-Z]/.test(value)) {
                        inputForm.setValue('input', value);
                      } else {
                        const formatted = formatInput(value);
                        inputForm.setValue('input', formatted);
                      }
                    }}
                    onPaste={(e) => {
                      e.preventDefault();
                      const pastedText = e.clipboardData.getData('text');
                      // Only format if it's not an email
                      if (pastedText.includes('@') || /[a-zA-Z]/.test(pastedText)) {
                        inputForm.setValue('input', pastedText);
                      } else {
                        const formatted = formatInput(pastedText);
                        inputForm.setValue('input', formatted);
                      }
                    }}
                  />
                  {getInputIcon()}
                </div>
                {inputForm.formState.errors.input && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {inputForm.formState.errors.input.message}
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
                    Отправка кода...
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
                      : showManualCodeRequest
                        ? 'Пользователь уже зарегистрирован. Введите код, отправленный ранее, или запросите новый код.'
                        : isWaitingForExistingCode 
                          ? `Введите код из предыдущего ${authMethod === 'email' ? 'email' : 'SMS'}` 
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
                    placeholder="000000"
                    maxLength={6}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-center text-2xl font-mono tracking-widest transition-all"
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '').slice(0, 6);
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

              {/* Resend code section */}
              <div className="text-center">
                {showManualCodeRequest ? (
                  <div className="space-y-3">
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      Если вы забыли код или он не приходит:
                    </p>
                    <button
                      onClick={() => forceSendCodeMutation.mutate()}
                      disabled={forceSendCodeMutation.isLoading}
                      className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto transition-colors"
                    >
                      <RotateCcw className="h-4 w-4 mr-1" />
                      {forceSendCodeMutation.isLoading ? 'Отправка...' : 'Отправить новый код'}
                    </button>
                  </div>
                ) : isWaitingForExistingCode ? (
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

              {/* Back to input */}
              <div className="text-center">
                <button
                  onClick={handleBackToInput}
                  className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-sm transition-colors"
                >
                  ← Изменить номер телефона или email
                </button>
              </div>
            </div>
          )}

          {/* Google OAuth - only show on input step */}
          {step === 'input' && (
            <>
              {/* Separator */}
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">ИЛИ</span>
                </div>
              </div>

              {/* Google OAuth button */}
              <button
                onClick={handleGoogleAuth}
                disabled={googleAuthMutation.isLoading}
                className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-3 px-4 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
              >
                {googleAuthMutation.isLoading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600 mr-2"></div>
                ) : (
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                )}
                Войти через Google
              </button>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            Нажимая "Войти", вы соглашаетесь с условиями использования
          </p>
        </div>
      </div>
      
      {/* Version info */}
              <div className="fixed bottom-2 right-2 text-xs text-red-600 bg-yellow-200 px-3 py-2 rounded shadow-lg border-2 border-red-500 font-bold">
                v1.2.3 - SMS ИСПРАВЛЕН - {new Date().toLocaleString()}
              </div>
    </div>
  );
};

export default UnifiedAuthPage;
