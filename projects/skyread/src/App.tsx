/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, History, ChevronLeft, Moon, Sun, Star, Info, LayoutGrid } from 'lucide-react';
import { ZODIAC_SIGNS } from './constants';
import { generateDailyHoroscope, HoroscopeData } from './services/geminiService';

type Screen = 'welcome' | 'home' | 'archive';
type Language = 'en' | 'zh';

const TRANSLATIONS = {
  en: {
    welcome: "Select your sun sign",
    dailyReading: "Daily Reading",
    skyExplainer: "Sky Explainer",
    skySnapshot: "Sky Snapshot",
    archive: "Archive",
    today: "Today",
    change: "Change",
    readingStars: "Reading the stars...",
    noReadings: "No readings saved yet.",
    loadingMessages: [
      "Consulting the celestial charts...",
      "Tracing planetary alignments...",
      "Decoding cosmic vibrations...",
      "Mapping the current sky...",
      "Translating the language of stars...",
      "Gleaning insights from the void..."
    ]
  },
  zh: {
    welcome: "选择你的星座",
    dailyReading: "每日运势",
    skyExplainer: "星象解析",
    skySnapshot: "星空快照",
    archive: "档案",
    today: "今日",
    change: "更换",
    readingStars: "正在解读星象...",
    noReadings: "尚无保存的记录。",
    loadingMessages: [
      "正在查阅天体图...",
      "正在追踪行星排列...",
      "正在解码宇宙共振...",
      "正在绘制当前星空...",
      "正在翻译星之语言...",
      "正在从虚空中获取洞见..."
    ]
  }
};

export default function App() {
  const [userSign, setUserSign] = useState<string | null>(localStorage.getItem('skyread_sign'));
  const [language, setLanguage] = useState<Language>(() => (localStorage.getItem('skyread_lang') as Language) || 'en');
  const [currentScreen, setCurrentScreen] = useState<Screen>(userSign ? 'home' : 'welcome');
  const [todayReading, setTodayReading] = useState<HoroscopeData | null>(null);
  const [archive, setArchive] = useState<HoroscopeData[]>(() => {
    const saved = localStorage.getItem('skyread_archive');
    return saved ? JSON.parse(saved) : [];
  });
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState(TRANSLATIONS[language].readingStars);
  const [selectedArchiveItem, setSelectedArchiveItem] = useState<HoroscopeData | null>(null);

  const t = TRANSLATIONS[language];

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (loading) {
      let i = 0;
      interval = setInterval(() => {
        setLoadingMessage(t.loadingMessages[i % t.loadingMessages.length]);
        i++;
      }, 2500);
    }
    return () => clearInterval(interval);
  }, [loading, language]);

  useEffect(() => {
    if (userSign && currentScreen === 'home') {
      fetchDailyReading(userSign, language);
    }
  }, [userSign, currentScreen, language]);

  const fetchDailyReading = async (sign: string, lang: Language) => {
    const today = new Date().toISOString().split('T')[0];
    const cacheKey = `${today}_${sign}_${lang}`;
    
    // Check if we already have today's reading in archive for this language
    // We'll store a unique identifier in the archive items or just check date/sign/content language
    // For simplicity, let's just check if todayReading matches the requested language
    if (todayReading && todayReading.date === today && (lang === 'zh' ? /[\u4e00-\u9fa5]/.test(todayReading.reading) : !/[\u4e00-\u9fa5]/.test(todayReading.reading))) {
       return;
    }

    setLoading(true);
    try {
      const data = await generateDailyHoroscope(sign, lang);
      setTodayReading(data);
      // We don't want to duplicate archive entries if just language changed, 
      // but for this app, let's just save the latest one.
      const newArchive = [data, ...archive.filter(item => item.date !== today || item.reading !== data.reading)].slice(0, 30);
      setArchive(newArchive);
      localStorage.setItem('skyread_archive', JSON.stringify(newArchive));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const toggleLanguage = () => {
    const newLang = language === 'en' ? 'zh' : 'en';
    setLanguage(newLang);
    localStorage.setItem('skyread_lang', newLang);
    setTodayReading(null); // Force re-fetch for new language
  };

  const handleSignSelect = (sign: string) => {
    setUserSign(sign);
    localStorage.setItem('skyread_sign', sign);
    setCurrentScreen('home');
  };

  const resetSign = () => {
    localStorage.removeItem('skyread_sign');
    setUserSign(null);
    setTodayReading(null);
    setCurrentScreen('welcome');
  };

  return (
    <div className="max-w-md mx-auto min-h-screen relative overflow-x-hidden font-sans">
      <CelestialBackground />
      
      <AnimatePresence mode="wait">
        {currentScreen === 'welcome' && (
          <WelcomeScreen key="welcome" onSelect={handleSignSelect} t={t} />
        )}

        {currentScreen === 'home' && (
          <HomeScreen 
            key="home"
            sign={userSign!} 
            data={todayReading}
            loading={loading}
            loadingMessage={loadingMessage}
            onNavigateToArchive={() => setCurrentScreen('archive')}
            onReset={resetSign}
            language={language}
            onToggleLanguage={toggleLanguage}
            t={t}
          />
        )}

        {currentScreen === 'archive' && (
          <ArchiveScreen 
            key="archive"
            archive={archive}
            onBack={() => {
              if (selectedArchiveItem) setSelectedArchiveItem(null);
              else setCurrentScreen('home');
            }}
            onGoHome={() => {
              setSelectedArchiveItem(null);
              setCurrentScreen('home');
            }}
            selectedItem={selectedArchiveItem}
            onSelectItem={setSelectedArchiveItem}
            t={t}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function CelestialBackground() {
  return (
    <div className="celestial-bg">
      {[...Array(50)].map((_, i) => (
        <div 
          key={i}
          className="star"
          style={{
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            width: `${Math.random() * 3}px`,
            height: `${Math.random() * 3}px`,
            '--duration': `${2 + Math.random() * 4}s`
          } as any}
        />
      ))}
    </div>
  );
}

function WelcomeScreen({ onSelect, t }: { onSelect: (sign: string) => void; t: any; key?: string }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="p-6 pt-20 flex flex-col items-center"
    >
      <div className="mb-8 text-center">
        <h1 className="text-5xl font-serif glow-text mb-2 italic">Skyread</h1>
        <p className="text-white/60 text-sm uppercase tracking-widest">{t.welcome}</p>
      </div>

      <div className="grid grid-cols-3 gap-4 w-full">
        {ZODIAC_SIGNS.map((sign) => (
          <motion.button
            key={sign.name}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onSelect(sign.name)}
            className="glass-card p-4 flex flex-col items-center justify-center aspect-square transition-colors hover:bg-white/10"
          >
            <span className="text-3xl mb-1">{sign.symbol}</span>
            <span className="text-[10px] uppercase tracking-tighter font-semibold opacity-80">{sign.name}</span>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

function HomeScreen({ sign, data, loading, loadingMessage, onNavigateToArchive, onReset, language, onToggleLanguage, t }: { 
  sign: string; 
  data: HoroscopeData | null; 
  loading: boolean;
  loadingMessage: string;
  onNavigateToArchive: () => void;
  onReset: () => void;
  language: Language;
  onToggleLanguage: () => void;
  t: any;
  key?: string;
}) {
  const signData = ZODIAC_SIGNS.find(s => s.name === sign);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="p-6 pb-24"
    >
      <header className="flex justify-between items-center mb-10">
        <button 
          onClick={onReset} 
          className="flex items-center gap-2 glass-card px-3 py-2 hover:bg-white/10 transition-colors group"
          title="Change Sign"
        >
          <span className="text-xl group-hover:scale-110 transition-transform">{signData?.symbol}</span>
          <div className="text-left">
            <h2 className="text-[10px] font-bold uppercase tracking-widest leading-none">{sign}</h2>
            <p className="text-[8px] opacity-50 uppercase">{t.change}</p>
          </div>
        </button>
        
        <div className="flex items-center gap-2">
          <button 
            onClick={onToggleLanguage}
            className="px-3 py-2 glass-card rounded-full hover:bg-white/10 transition-colors text-[10px] font-bold uppercase tracking-widest"
          >
            {language === 'en' ? 'ZH' : 'EN'}
          </button>
          <button 
            onClick={onNavigateToArchive}
            className="p-3 glass-card rounded-full hover:bg-white/10 transition-colors"
          >
            <History size={20} />
          </button>
        </div>
      </header>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <motion.div 
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          >
            <Sparkles size={40} className="text-white/40" />
          </motion.div>
          <p className="text-white/40 text-sm animate-pulse tracking-widest uppercase text-center px-4">{loadingMessage}</p>
        </div>
      ) : data ? (
        <div className="space-y-8">
          <section>
            <div className="flex items-center gap-2 mb-4 opacity-40">
              <Sun size={14} />
              <span className="text-[10px] uppercase tracking-[0.2em] font-bold">{t.dailyReading}</span>
            </div>
            <h3 className="text-3xl font-serif italic glow-text mb-4 leading-tight">
              {new Date().toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US', { month: 'long', day: 'numeric' })}
            </h3>
            <p className="text-lg leading-relaxed text-white/90 font-light">
              {data.reading}
            </p>
          </section>

          <section className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4 opacity-50">
              <Info size={14} />
              <span className="text-[10px] uppercase tracking-[0.2em] font-bold">{t.skyExplainer}</span>
            </div>
            <p className="text-sm leading-relaxed text-white/70">
              {data.skyExplainer}
            </p>
          </section>

          <section>
            <div className="flex items-center gap-2 mb-6 opacity-40">
              <LayoutGrid size={14} />
              <span className="text-[10px] uppercase tracking-[0.2em] font-bold">{t.skySnapshot}</span>
            </div>
            <div className="grid grid-cols-1 gap-4">
              {data.snapshot.map((item, i) => (
                <div key={i} className="flex items-center justify-between border-b border-white/5 pb-4">
                  <div>
                    <h4 className="text-sm font-bold text-white/90">{item.planet}</h4>
                    <p className="text-[10px] text-white/40 uppercase tracking-widest">{item.position}</p>
                  </div>
                  <p className="text-xs text-right text-white/60 italic max-w-[150px]">
                    {item.influence}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </motion.div>
  );
}

function ArchiveScreen({ archive, onBack, onGoHome, selectedItem, onSelectItem, t }: { 
  archive: HoroscopeData[]; 
  onBack: () => void;
  onGoHome: () => void;
  selectedItem: HoroscopeData | null;
  onSelectItem: (item: HoroscopeData | null) => void;
  t: any;
  key?: string;
}) {
  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-6"
    >
      <header className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="p-2 glass-card rounded-full hover:bg-white/10 transition-colors"
          >
            <ChevronLeft size={20} />
          </button>
          <h2 className="text-xl font-serif italic glow-text">{t.archive}</h2>
        </div>
        <button 
          onClick={onGoHome}
          className="p-2 glass-card rounded-full hover:bg-white/10 transition-colors flex items-center gap-2 px-4"
        >
          <Sun size={16} />
          <span className="text-[10px] uppercase font-bold tracking-widest">{t.today}</span>
        </button>
      </header>

      {selectedItem ? (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <section>
            <h3 className="text-3xl font-serif italic glow-text mb-4">
              {new Date(selectedItem.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </h3>
            <p className="text-lg leading-relaxed text-white/90 font-light">
              {selectedItem.reading}
            </p>
          </section>

          <div className="glass-card p-6">
            <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold opacity-50 mb-3">Sky Explainer</h4>
            <p className="text-sm text-white/70 leading-relaxed">{selectedItem.skyExplainer}</p>
          </div>

          <div className="space-y-4">
            <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold opacity-50">Snapshot</h4>
            {selectedItem.snapshot.map((item, i) => (
              <div key={i} className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-xs font-bold">{item.planet}</span>
                <span className="text-[10px] opacity-50">{item.position}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {archive.length === 0 ? (
            <p className="text-center text-white/40 py-20 italic">{t.noReadings}</p>
          ) : (
            archive.map((item, i) => (
              <motion.button
                key={i}
                whileTap={{ scale: 0.98 }}
                onClick={() => onSelectItem(item)}
                className="w-full glass-card p-5 text-left flex justify-between items-center group hover:bg-white/10 transition-colors"
              >
                <div>
                  <h3 className="text-lg font-serif italic mb-1">
                    {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </h3>
                  <p className="text-xs text-white/40 line-clamp-1">{item.reading}</p>
                </div>
                <ChevronLeft size={16} className="rotate-180 opacity-20 group-hover:opacity-100 transition-opacity" />
              </motion.button>
            ))
          )}
        </div>
      )}
    </motion.div>
  );
}
