'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import gsap from 'gsap';
import { ArrowRight, Download, Code, Palette, Zap } from 'lucide-react';

const stats = [
  { value: 3, suffix: '+', label: '年经验' },
  { value: 10, suffix: '+', label: '个项目' },
  { value: 5, suffix: '+', label: '技术栈' },
];

const roles = ['Web 开发者', 'UI 设计师', '游戏开发者', '全栈工程师'];

export default function Hero() {
  const typingRef = useRef<HTMLSpanElement>(null);
  const roleIndex = useRef(0);
  const charIndex = useRef(0);
  const isDeleting = useRef(false);

  useEffect(() => {
    const el = typingRef.current;
    if (!el) return;

    const type = () => {
      const word = roles[roleIndex.current];

      if (isDeleting.current) {
        el.textContent = word.substring(0, charIndex.current - 1);
        charIndex.current--;
      } else {
        el.textContent = word.substring(0, charIndex.current + 1);
        charIndex.current++;
      }

      let speed = isDeleting.current ? 40 : 80;

      if (!isDeleting.current && charIndex.current === word.length) {
        speed = 2500;
        isDeleting.current = true;
      } else if (isDeleting.current && charIndex.current === 0) {
        isDeleting.current = false;
        roleIndex.current = (roleIndex.current + 1) % roles.length;
        speed = 400;
      }

      setTimeout(type, speed);
    };

    const timer = setTimeout(type, 1200);
    return () => clearTimeout(timer);
  }, []);

  // GSAP animations
  useEffect(() => {
    if (typeof gsap === 'undefined') return;

    const tl = gsap.timeline({ delay: 0.5 });

    tl.from('.hero-tag', { opacity: 0, y: 30, duration: 0.8, ease: 'power3.out' })
      .from('.hero-title-line', { opacity: 0, y: 40, stagger: 0.15, duration: 0.8, ease: 'power3.out' }, '-=0.4')
      .from('.hero-desc', { opacity: 0, y: 30, duration: 0.7, ease: 'power3.out' }, '-=0.3')
      .from('.hero-btn', { opacity: 0, y: 20, stagger: 0.15, duration: 0.6, ease: 'power3.out' }, '-=0.3')
      .from('.hero-stat', { opacity: 0, y: 20, stagger: 0.1, duration: 0.6, ease: 'power3.out' }, '-=0.3')
      .from('.hero-visual', { opacity: 0, x: 60, duration: 1, ease: 'power3.out' }, '-=0.8');
  }, []);

  return (
    <section id="home" className="min-h-screen flex items-center relative overflow-hidden pt-32 pb-20">
      {/* Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="mesh-gradient" />
        <div className="hero-glow-1 absolute w-[500px] h-[500px] rounded-full bg-[var(--accent)] opacity-8 blur-[80px] top-[-10%] right-[10%] animate-float" />
        <div className="hero-glow-2 absolute w-[400px] h-[400px] rounded-full bg-[var(--gold)] opacity-6 blur-[80px] bottom-[-10%] left-[5%] animate-float-reverse" />
      </div>

      <div className="max-w-[var(--container-max)] mx-auto px-6 grid grid-cols-1 lg:grid-cols-[1fr_0.8fr] gap-20 items-center relative z-10">
        {/* Left Content */}
        <div>
          <motion.div
            className="hero-tag inline-flex items-center gap-2 px-4 py-1.5 bg-[var(--accent-dim)] border border-[rgba(212,98,42,0.15)] rounded-full font-['var(--font-mono)'] text-xs text-[var(--accent)] mb-7"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
          >
            <span className="w-1.5 h-1.5 bg-[var(--accent)] rounded-full animate-pulse" />
            可远程协作 · 全栈开发
          </motion.div>

          <h1 className="hero-title font-['var(--font-noto)'] leading-[1.1] mb-6">
            <span className="hero-title-line block text-xl text-[var(--text-secondary)] mb-2 font-['var(--font-inter)']">
              你好，我是
            </span>
            <span className="hero-title-line block text-5xl lg:text-7xl font-bold">
              <span className="text-[var(--text-primary)]">李宿</span>
              <span className="ml-4 font-['var(--font-mono)'] text-2xl lg:text-3xl font-normal text-[var(--text-muted)] tracking-[2px]">
                lisu
              </span>
            </span>
            <span className="hero-title-line block font-['var(--font-mono)'] text-2xl lg:text-3xl font-bold text-[var(--accent)] mt-1 min-h-[2.8rem]">
              <span ref={typingRef}></span>
              <span className="font-extralight animate-blink">|</span>
            </span>
          </h1>

          <p className="hero-desc text-lg text-[var(--text-secondary)] leading-relaxed mb-9 max-w-lg">
            热爱创造优雅的 Web 体验，专注于前端开发、UI 设计和游戏开发。
            用代码构建有温度的产品。
          </p>

          <div className="hero-actions flex gap-4 mb-12 flex-wrap">
            <a href="#projects" className="hero-btn btn btn-primary">
              查看项目 <ArrowRight size={18} />
            </a>
            <a href="/resume.pdf" className="hero-btn btn btn-ghost" download>
              下载简历 <Download size={18} />
            </a>
          </div>

          <div className="hero-stats flex gap-10">
            {stats.map((stat, i) => (
              <div key={i} className="hero-stat flex flex-col">
                <span className="font-['var(--font-mono)'] text-4xl font-bold leading-none">
                  {stat.value}{stat.suffix}
                </span>
                <span className="text-xs text-[var(--text-muted)] mt-1 tracking-wider">
                  {stat.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Visual */}
        <div className="hero-visual hidden lg:flex justify-center">
          <div className="relative w-[360px]">
            <div className="relative rounded-2xl overflow-hidden border border-[var(--border-light)] aspect-[3/4] bg-gradient-to-br from-[var(--bg-elevated)] to-[var(--bg-card)]">
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 text-[var(--text-muted)]">
                <Code size={48} className="text-[var(--accent)]" />
                <span className="font-['var(--font-noto)'] text-2xl font-bold text-[var(--text-primary)]">
                  全栈开发
                </span>
                <div className="flex gap-4">
                  <Palette size={20} className="text-[var(--gold)]" />
                  <Zap size={20} className="text-[var(--accent)]" />
                  <Code size={20} className="text-[var(--jade)]" />
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-[var(--bg-primary)]/60 to-transparent" />
            </div>
            <div className="absolute -top-3 -right-3 w-full h-full border-2 border-[var(--accent)] rounded-2xl opacity-20 -z-10 transition-all group-hover:opacity-40" />
            <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-5 py-2 bg-[var(--bg-card)] border border-[var(--border-light)] rounded-full font-['var(--font-mono)'] text-xs text-[var(--text-secondary)] whitespace-nowrap shadow-lg">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              可远程协作
            </div>
          </div>
        </div>
      </div>

      {/* Scroll hint */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-[var(--text-muted)]"
        animate={{ y: [0, 10, 0] }}
        transition={{ repeat: Infinity, duration: 2 }}
      >
        <span className="text-xs tracking-widest uppercase">Scroll</span>
        <div className="w-5 h-8 border-2 border-[var(--text-muted)] rounded-full flex justify-center pt-1">
          <div className="w-1 h-2 bg-[var(--text-muted)] rounded-full animate-bounce" />
        </div>
      </motion.div>
    </section>
  );
}
