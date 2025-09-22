import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface Language {
  code: string;
  name: string;
  nativeName: string;
}

export const languages: Language[] = [
  { code: 'kk', name: 'Kazakh', nativeName: 'Қазақша' },
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский' }
];

export interface Translations {
  // Navigation
  home: string;
  explore: string;
  profile: string;
  search: string;
  notifications: string;
  settings: string;
  logout: string;
  
  // Authentication
  login: string;
  register: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone: string;
  forgotPassword: string;
  rememberMe: string;
  signInWithGoogle: string;
  signInWithPhone: string;
  signInWithEmail: string;
  
  // Posts
  createPost: string;
  writeSomething: string;
  addPhoto: string;
  addVideo: string;
  post: string;
  like: string;
  comment: string;
  share: string;
  delete: string;
  edit: string;
  
  // Comments
  writeComment: string;
  comments: string;
  reply: string;
  
  // Profile
  editProfile: string;
  followers: string;
  following: string;
  posts: string;
  bio: string;
  location: string;
  website: string;
  joinDate: string;
  
  // Search
  searchPlaceholder: string;
  searchResults: string;
  noResults: string;
  
  // Notifications
  newNotification: string;
  likedYourPost: string;
  commentedOnYourPost: string;
  startedFollowingYou: string;
  
  // AI Features
  generateDescription: string;
  generateHashtags: string;
  enhanceContent: string;
  autoGeneratePost: string;
  aiDescription: string;
  aiHashtags: string;
  aiEnhanced: string;
  
  // Common
  save: string;
  cancel: string;
  confirm: string;
  loading: string;
  error: string;
  success: string;
  yes: string;
  no: string;
  close: string;
  back: string;
  next: string;
  previous: string;
  more: string;
  less: string;
  
  // Time
  now: string;
  minutesAgo: string;
  hoursAgo: string;
  daysAgo: string;
  weeksAgo: string;
  monthsAgo: string;
  yearsAgo: string;
}

const translations: Record<string, Translations> = {
  kk: {
    // Navigation
    home: 'Басты бет',
    explore: 'Зерттеу',
    profile: 'Профиль',
    search: 'Іздеу',
    notifications: 'Хабарландырулар',
    settings: 'Баптаулар',
    logout: 'Шығу',
    
    // Authentication
    login: 'Кіру',
    register: 'Тіркелу',
    email: 'Электрондық пошта',
    password: 'Құпия сөз',
    confirmPassword: 'Құпия сөзді растау',
    phone: 'Телефон',
    forgotPassword: 'Құпия сөзді ұмыттыңыз ба?',
    rememberMe: 'Мені есте сақтау',
    signInWithGoogle: 'Google арқылы кіру',
    signInWithPhone: 'Телефон арқылы кіру',
    signInWithEmail: 'Электрондық пошта арқылы кіру',
    
    // Posts
    createPost: 'Жазба жасау',
    writeSomething: 'Бірдеңе жазыңыз...',
    addPhoto: 'Фото қосу',
    addVideo: 'Видео қосу',
    post: 'Жариялау',
    like: 'Ұнату',
    comment: 'Пікір',
    share: 'Бөлісу',
    delete: 'Жою',
    edit: 'Өңдеу',
    
    // Comments
    writeComment: 'Пікір жазыңыз...',
    comments: 'Пікірлер',
    reply: 'Жауап беру',
    
    // Profile
    editProfile: 'Профильді өңдеу',
    followers: 'Жазылушылар',
    following: 'Жазылғандар',
    posts: 'Жазбалар',
    bio: 'Биография',
    location: 'Орналасқан жері',
    website: 'Веб-сайт',
    joinDate: 'Қосылған күні',
    
    // Search
    searchPlaceholder: 'Іздеу...',
    searchResults: 'Іздеу нәтижелері',
    noResults: 'Нәтиже табылмады',
    
    // Notifications
    newNotification: 'Жаңа хабарландыру',
    likedYourPost: 'Сіздің жазбаңызды ұнатты',
    commentedOnYourPost: 'Сіздің жазбаңызға пікір қалдырды',
    startedFollowingYou: 'Сізге жазыла бастады',
    
    // AI Features
    generateDescription: 'Сипаттама жасау',
    generateHashtags: 'Хэштегтер жасау',
    enhanceContent: 'Мазмұнды жақсарту',
    autoGeneratePost: 'Автоматты жазба жасау',
    aiDescription: 'AI сипаттамасы',
    aiHashtags: 'AI хэштегтері',
    aiEnhanced: 'AI жақсартылған',
    
    // Common
    save: 'Сақтау',
    cancel: 'Болдырмау',
    confirm: 'Растау',
    loading: 'Жүктелуде...',
    error: 'Қате',
    success: 'Сәтті',
    yes: 'Иә',
    no: 'Жоқ',
    close: 'Жабу',
    back: 'Артқа',
    next: 'Келесі',
    previous: 'Алдыңғы',
    more: 'Көбірек',
    less: 'Азырақ',
    
    // Time
    now: 'Қазір',
    minutesAgo: 'минут бұрын',
    hoursAgo: 'сағат бұрын',
    daysAgo: 'күн бұрын',
    weeksAgo: 'апта бұрын',
    monthsAgo: 'ай бұрын',
    yearsAgo: 'жыл бұрын'
  },
  
  en: {
    // Navigation
    home: 'Home',
    explore: 'Explore',
    profile: 'Profile',
    search: 'Search',
    notifications: 'Notifications',
    settings: 'Settings',
    logout: 'Logout',
    
    // Authentication
    login: 'Login',
    register: 'Register',
    email: 'Email',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    phone: 'Phone',
    forgotPassword: 'Forgot Password?',
    rememberMe: 'Remember Me',
    signInWithGoogle: 'Sign in with Google',
    signInWithPhone: 'Sign in with Phone',
    signInWithEmail: 'Sign in with Email',
    
    // Posts
    createPost: 'Create Post',
    writeSomething: 'Write something...',
    addPhoto: 'Add Photo',
    addVideo: 'Add Video',
    post: 'Post',
    like: 'Like',
    comment: 'Comment',
    share: 'Share',
    delete: 'Delete',
    edit: 'Edit',
    
    // Comments
    writeComment: 'Write a comment...',
    comments: 'Comments',
    reply: 'Reply',
    
    // Profile
    editProfile: 'Edit Profile',
    followers: 'Followers',
    following: 'Following',
    posts: 'Posts',
    bio: 'Bio',
    location: 'Location',
    website: 'Website',
    joinDate: 'Joined',
    
    // Search
    searchPlaceholder: 'Search...',
    searchResults: 'Search Results',
    noResults: 'No results found',
    
    // Notifications
    newNotification: 'New Notification',
    likedYourPost: 'liked your post',
    commentedOnYourPost: 'commented on your post',
    startedFollowingYou: 'started following you',
    
    // AI Features
    generateDescription: 'Generate Description',
    generateHashtags: 'Generate Hashtags',
    enhanceContent: 'Enhance Content',
    autoGeneratePost: 'Auto Generate Post',
    aiDescription: 'AI Description',
    aiHashtags: 'AI Hashtags',
    aiEnhanced: 'AI Enhanced',
    
    // Common
    save: 'Save',
    cancel: 'Cancel',
    confirm: 'Confirm',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    yes: 'Yes',
    no: 'No',
    close: 'Close',
    back: 'Back',
    next: 'Next',
    previous: 'Previous',
    more: 'More',
    less: 'Less',
    
    // Time
    now: 'now',
    minutesAgo: 'minutes ago',
    hoursAgo: 'hours ago',
    daysAgo: 'days ago',
    weeksAgo: 'weeks ago',
    monthsAgo: 'months ago',
    yearsAgo: 'years ago'
  },
  
  ru: {
    // Navigation
    home: 'Главная',
    explore: 'Исследовать',
    profile: 'Профиль',
    search: 'Поиск',
    notifications: 'Уведомления',
    settings: 'Настройки',
    logout: 'Выйти',
    
    // Authentication
    login: 'Войти',
    register: 'Регистрация',
    email: 'Электронная почта',
    password: 'Пароль',
    confirmPassword: 'Подтвердить пароль',
    phone: 'Телефон',
    forgotPassword: 'Забыли пароль?',
    rememberMe: 'Запомнить меня',
    signInWithGoogle: 'Войти через Google',
    signInWithPhone: 'Войти через телефон',
    signInWithEmail: 'Войти через email',
    
    // Posts
    createPost: 'Создать пост',
    writeSomething: 'Напишите что-нибудь...',
    addPhoto: 'Добавить фото',
    addVideo: 'Добавить видео',
    post: 'Опубликовать',
    like: 'Нравится',
    comment: 'Комментарий',
    share: 'Поделиться',
    delete: 'Удалить',
    edit: 'Редактировать',
    
    // Comments
    writeComment: 'Написать комментарий...',
    comments: 'Комментарии',
    reply: 'Ответить',
    
    // Profile
    editProfile: 'Редактировать профиль',
    followers: 'Подписчики',
    following: 'Подписки',
    posts: 'Посты',
    bio: 'О себе',
    location: 'Местоположение',
    website: 'Веб-сайт',
    joinDate: 'Присоединился',
    
    // Search
    searchPlaceholder: 'Поиск...',
    searchResults: 'Результаты поиска',
    noResults: 'Результаты не найдены',
    
    // Notifications
    newNotification: 'Новое уведомление',
    likedYourPost: 'понравился ваш пост',
    commentedOnYourPost: 'прокомментировал ваш пост',
    startedFollowingYou: 'начал подписываться на вас',
    
    // AI Features
    generateDescription: 'Сгенерировать описание',
    generateHashtags: 'Сгенерировать хэштеги',
    enhanceContent: 'Улучшить контент',
    autoGeneratePost: 'Автогенерация поста',
    aiDescription: 'AI описание',
    aiHashtags: 'AI хэштеги',
    aiEnhanced: 'AI улучшенный',
    
    // Common
    save: 'Сохранить',
    cancel: 'Отмена',
    confirm: 'Подтвердить',
    loading: 'Загрузка...',
    error: 'Ошибка',
    success: 'Успешно',
    yes: 'Да',
    no: 'Нет',
    close: 'Закрыть',
    back: 'Назад',
    next: 'Далее',
    previous: 'Предыдущий',
    more: 'Больше',
    less: 'Меньше',
    
    // Time
    now: 'сейчас',
    minutesAgo: 'минут назад',
    hoursAgo: 'часов назад',
    daysAgo: 'дней назад',
    weeksAgo: 'недель назад',
    monthsAgo: 'месяцев назад',
    yearsAgo: 'лет назад'
  }
};

interface LanguageContextType {
  language: string;
  setLanguage: (language: string) => void;
  t: Translations;
  languages: Language[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

interface LanguageProviderProps {
  children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [language, setLanguage] = useState<string>(() => {
    // Get language from localStorage or default to 'ru'
    return localStorage.getItem('language') || 'ru';
  });

  useEffect(() => {
    // Save language to localStorage
    localStorage.setItem('language', language);
  }, [language]);

  const t = translations[language] || translations['ru'];

  const value: LanguageContextType = {
    language,
    setLanguage,
    t,
    languages
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export default LanguageContext;
