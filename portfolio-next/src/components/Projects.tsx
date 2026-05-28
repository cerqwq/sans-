'use client';

import { motion, useInView } from 'framer-motion';
import { useRef, useState } from 'react';
import { ExternalLink, Eye, Code, Gamepad2, Sparkles, Globe } from 'lucide-react';

const projects = [
  {
    title: '鬼谷修仙录',
    desc: '水墨风格文字修仙游戏，Flask + Canvas 前端，支持战斗、探索、炼丹等系统',
    icon: Gamepad2,
    tags: ['Python', 'Flask', 'Canvas', 'SQLite'],
    category: 'game',
    link: '/xiuxian',
    github: 'https://github.com/cerqwq/sans-/tree/main/xiuxian',
    color: 'var(--jade)',
    features: ['水墨风格 UI', '实时战斗系统', '炼丹系统', '宗门系统'],
  },
  {
    title: '斗地主在线',
    desc: '在线斗地主游戏，Flask + WebSocket 实时对战，支持 AI 对手',
    icon: Gamepad2,
    tags: ['Python', 'Flask', 'WebSocket', 'SQLite'],
    category: 'game',
    link: '/ddz',
    github: 'https://github.com/cerqwq/sans-/tree/main/ddz',
    color: 'var(--gold)',
    features: ['实时对战', 'AI 对手', '卡牌动画', '聊天系统'],
  },
  {
    title: '手势粒子特效',
    desc: '基于 MediaPipe 手势识别的 Canvas 粒子特效，支持多种手势控制',
    icon: Sparkles,
    tags: ['JavaScript', 'Canvas', 'MediaPipe', 'WebGL'],
    category: 'creative',
    link: '/hand-particles',
    github: 'https://github.com/cerqwq/sans-/tree/main/hand-particles',
    color: 'var(--accent)',
    features: ['手势识别', '粒子系统', '多种特效', '实时渲染'],
  },
  {
    title: '个人作品集',
    desc: 'Next.js + Tailwind CSS 构建的现代作品集网站，支持暗色模式',
    icon: Globe,
    tags: ['Next.js', 'React', 'Tailwind', 'GSAP'],
    category: 'web',
    link: '/',
    github: 'https://github.com/cerqwq/sans-/tree/main/portfolio-next',
    color: 'var(--violet)',
    features: ['响应式设计', 'GSAP 动画', '暗色模式', 'SEO 优化'],
  },
];

const filters = [
  { key: 'all', label: '全部' },
  { key: 'game', label: '游戏' },
  { key: 'web', label: 'Web' },
  { key: 'creative', label: '创意' },
];

export default function Projects() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [activeFilter, setActiveFilter] = useState('all');

  const filteredProjects = activeFilter === 'all'
    ? projects
    : projects.filter(p => p.category === activeFilter);

  return (
    <section id="projects" className="py-32 bg-[var(--bg-secondary)]" ref={ref}>
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
            <span>作品集</span>
          </div>
          <h2 className="section-title">
            精选项目<span className="text-[var(--accent)]">.</span>
          </h2>
          <p className="section-desc">
            以下是我参与开发的一些项目，涵盖游戏、Web 应用和创意实验。
          </p>
        </motion.div>

        {/* Filters */}
        <motion.div
          className="flex justify-center gap-2 mb-12 flex-wrap"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {filters.map(f => (
            <button
              key={f.key}
              onClick={() => setActiveFilter(f.key)}
              className={`px-5 py-2 rounded-full text-sm font-medium transition-all ${
                activeFilter === f.key
                  ? 'bg-[var(--accent)] text-[var(--bg-primary)]'
                  : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-[var(--border)]'
              }`}
            >
              {f.label}
            </button>
          ))}
        </motion.div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredProjects.map((project, i) => (
            <motion.div
              key={project.title}
              className="glass-card overflow-hidden group"
              initial={{ opacity: 0, y: 60, scale: 0.95 }}
              animate={isInView ? { opacity: 1, y: 0, scale: 1 } : {}}
              transition={{
                duration: 0.9,
                delay: 0.3 + i * 0.15,
                ease: [0.16, 1, 0.3, 1],
              }}
              layout
            >
              {/* Project Image */}
              <div className="relative h-48 overflow-hidden bg-gradient-to-br from-[var(--bg-elevated)] to-[var(--bg-card)]">
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                  <project.icon size={48} style={{ color: project.color }} />
                  <span className="font-['var(--font-noto)'] text-lg font-bold">
                    {project.title}
                  </span>
                </div>
                <div className="absolute inset-0 bg-[var(--accent)]/90 flex items-center justify-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <a
                    href={project.link}
                    className="btn btn-primary text-sm"
                  >
                    <Eye size={16} /> 查看项目
                  </a>
                  <a
                    href={project.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-ghost text-sm"
                  >
                    <Code size={16} /> 源码
                  </a>
                </div>
              </div>

              {/* Project Info */}
              <div className="p-6">
                <div className="flex flex-wrap gap-2 mb-3">
                  {project.tags.map(tag => (
                    <span
                      key={tag}
                      className="px-2.5 py-0.5 bg-[var(--accent-dim)] text-[var(--accent)] rounded-full text-xs font-['var(--font-mono)']"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">
                  {project.title}
                </h3>
                <p className="text-sm text-[var(--text-muted)] mb-4 leading-relaxed">
                  {project.desc}
                </p>

                {/* Features */}
                <div className="flex flex-wrap gap-2">
                  {project.features.map(feature => (
                    <span
                      key={feature}
                      className="px-2 py-0.5 bg-[var(--bg-elevated)] text-[var(--text-secondary)] rounded text-xs"
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
