'use client';

import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

const skills = [
  {
    category: '前端',
    icon: '🎨',
    items: [
      { name: 'React / Next.js', level: 90 },
      { name: 'Vue / Nuxt', level: 85 },
      { name: 'TypeScript', level: 88 },
      { name: 'Tailwind CSS', level: 92 },
      { name: 'GSAP / Framer Motion', level: 80 },
    ],
  },
  {
    category: '后端',
    icon: '⚙️',
    items: [
      { name: 'Node.js / Express', level: 85 },
      { name: 'Python / Flask', level: 88 },
      { name: 'PostgreSQL / MongoDB', level: 82 },
      { name: 'Redis', level: 78 },
      { name: 'REST API / GraphQL', level: 85 },
    ],
  },
  {
    category: '工具',
    icon: '🛠️',
    items: [
      { name: 'Git / GitHub', level: 90 },
      { name: 'Docker', level: 75 },
      { name: 'VS Code', level: 95 },
      { name: 'Figma', level: 80 },
      { name: 'Webpack / Vite', level: 85 },
    ],
  },
  {
    category: '游戏',
    icon: '🎮',
    items: [
      { name: 'Canvas 2D', level: 88 },
      { name: 'Phaser 4', level: 75 },
      { name: 'WebGL / Three.js', level: 70 },
      { name: '游戏设计', level: 80 },
      { name: '动画系统', level: 85 },
    ],
  },
];

export default function Skills() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <section id="skills" className="py-32" ref={ref}>
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
            <span>技能栈</span>
          </div>
          <h2 className="section-title">
            技术能力<span className="text-[var(--accent)]">.</span>
          </h2>
          <p className="section-desc">
            持续学习，不断进步。以下是我在各个领域的技术能力。
          </p>
        </motion.div>

        {/* Skills Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {skills.map((category, catIdx) => (
            <motion.div
              key={catIdx}
              className="glass-card p-8"
              initial={{ opacity: 0, y: 60 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{
                duration: 0.8,
                delay: catIdx * 0.15,
                ease: [0.16, 1, 0.3, 1],
              }}
            >
              <div className="flex items-center gap-3 mb-6">
                <span className="text-2xl">{category.icon}</span>
                <h3 className="text-xl font-bold text-[var(--text-primary)]">
                  {category.category}
                </h3>
              </div>

              <div className="space-y-4">
                {category.items.map((skill, skillIdx) => (
                  <div key={skillIdx}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-[var(--text-secondary)]">
                        {skill.name}
                      </span>
                      <span className="font-['var(--font-mono)'] text-sm font-bold text-[var(--accent)]">
                        {skill.level}%
                      </span>
                    </div>
                    <div className="h-1 bg-[var(--bg-elevated)] rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-[var(--accent)] to-[var(--gold)] rounded-full"
                        initial={{ width: 0 }}
                        animate={isInView ? { width: `${skill.level}%` } : {}}
                        transition={{
                          duration: 1.5,
                          delay: 0.5 + catIdx * 0.15 + skillIdx * 0.1,
                          ease: [0.16, 1, 0.3, 1],
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
