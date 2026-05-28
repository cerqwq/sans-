'use client';

import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { Code, Palette, Zap, Globe, Database, Gamepad2 } from 'lucide-react';

const highlights = [
  {
    icon: Code,
    title: '前端开发',
    desc: 'React、Vue、Next.js、TypeScript，构建现代化 Web 应用',
    color: 'var(--accent)',
  },
  {
    icon: Palette,
    title: 'UI 设计',
    desc: '注重用户体验，创造优雅直观的界面设计',
    color: 'var(--gold)',
  },
  {
    icon: Zap,
    title: '性能优化',
    desc: '极致的性能优化，让应用流畅运行',
    color: 'var(--jade)',
  },
  {
    icon: Globe,
    title: '全栈能力',
    desc: 'Node.js、Python、Flask，前后端一体化开发',
    color: 'var(--violet)',
  },
  {
    icon: Database,
    title: '数据库',
    desc: 'PostgreSQL、MongoDB、Redis，数据驱动开发',
    color: 'var(--jade)',
  },
  {
    icon: Gamepad2,
    title: '游戏开发',
    desc: 'Canvas、Phaser、WebGL，创造互动游戏体验',
    color: 'var(--accent)',
  },
];

export default function About() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <section id="about" className="py-32 bg-[var(--bg-secondary)]" ref={ref}>
      <div className="max-w-[var(--container-max)] mx-auto px-6">
        {/* Section Header */}
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 60 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="section-tag">
            <span className="w-1.5 h-1.5 bg-[var(--accent)] rounded-full" />
            <span>关于我</span>
          </div>
          <h2 className="section-title">
            热爱创造<span className="text-[var(--accent)]">.</span>
          </h2>
          <p className="section-desc">
            全栈开发工程师，专注于 Web 开发、UI 设计和游戏开发。
            用代码构建有温度的产品，用设计创造优雅的体验。
          </p>
        </motion.div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
          {/* Left - Story */}
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="glass-card p-8">
              <h3 className="text-2xl font-bold mb-6 text-[var(--text-primary)]">
                我的故事
              </h3>
              <div className="space-y-4 text-[var(--text-secondary)] leading-relaxed">
                <p>
                  作为一名全栈开发工程师，我热爱用代码解决问题，用设计创造价值。
                  我相信技术的力量可以让世界变得更美好。
                </p>
                <p>
                  我的工作涵盖了从前端到后端的完整开发流程，
                  包括 React、Vue、Next.js、Node.js、Python 等技术栈。
                  我注重代码质量和用户体验，追求极致的性能优化。
                </p>
                <p>
                  除了工作，我还热爱游戏开发和创意编程。
                  我相信游戏是艺术与技术的完美结合，
                  可以创造独特的互动体验。
                </p>
              </div>
            </div>
          </motion.div>

          {/* Right - Highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {highlights.map((item, i) => (
              <motion.div
                key={i}
                className="glass-card p-6 group"
                initial={{ opacity: 0, y: 40 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8, delay: 0.3 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110 group-hover:-rotate-3"
                  style={{ background: `${item.color}15` }}
                >
                  <item.icon size={24} style={{ color: item.color }} />
                </div>
                <h4 className="text-lg font-bold text-[var(--text-primary)] mb-2">
                  {item.title}
                </h4>
                <p className="text-sm text-[var(--text-muted)] leading-relaxed">
                  {item.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
