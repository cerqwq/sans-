'use client';

import { motion, useInView } from 'framer-motion';
import { useRef, useState } from 'react';
import { Mail, Send, Code, MapPin, Clock, CheckCircle } from 'lucide-react';

const contactInfo = [
  { icon: Mail, label: '邮箱', value: '995935899@qq.com', href: 'mailto:995935899@qq.com' },
  { icon: Code, label: 'GitHub', value: 'github.com/cerqwq/sans-', href: 'https://github.com/cerqwq/sans-' },
  { icon: MapPin, label: '位置', value: '中国', href: null },
  { icon: Clock, label: '时区', value: 'UTC+8', href: null },
];

export default function Contact() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [formState, setFormState] = useState<'idle' | 'sending' | 'sent'>('idle');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormState('sending');

    // Simulate sending
    await new Promise(resolve => setTimeout(resolve, 1000));

    setFormState('sent');
    setTimeout(() => setFormState('idle'), 3000);
  };

  return (
    <section id="contact" className="py-32" ref={ref}>
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
            <span>联系我</span>
          </div>
          <h2 className="section-title">
            开始合作<span className="text-[var(--accent)]">.</span>
          </h2>
          <p className="section-desc">
            有项目想法？或者只是想聊聊？随时联系我。
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          {/* Contact Info */}
          <motion.div
            initial={{ opacity: 0, x: -60 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="glass-card p-8">
              <h3 className="text-2xl font-bold mb-6 text-[var(--text-primary)]">
                联系方式
              </h3>

              <div className="space-y-4">
                {contactInfo.map((item, i) => (
                  <div key={i} className="flex items-center gap-4 group">
                    <div className="w-12 h-12 rounded-xl bg-[var(--accent-dim)] flex items-center justify-center transition-transform group-hover:scale-110">
                      <item.icon size={20} className="text-[var(--accent)]" />
                    </div>
                    <div>
                      <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider">
                        {item.label}
                      </p>
                      {item.href ? (
                        <a
                          href={item.href}
                          target={item.href.startsWith('http') ? '_blank' : undefined}
                          rel={item.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                          className="text-[var(--text-primary)] hover:text-[var(--accent)] transition-colors"
                        >
                          {item.value}
                        </a>
                      ) : (
                        <p className="text-[var(--text-primary)]">{item.value}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 pt-6 border-t border-[var(--border)]">
                <p className="text-sm text-[var(--text-muted)] leading-relaxed">
                  我通常在 24 小时内回复。如果你有紧急需求，
                  请通过邮件或 GitHub 联系我。
                </p>
              </div>
            </div>
          </motion.div>

          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="glass-card p-8">
              <h3 className="text-2xl font-bold mb-6 text-[var(--text-primary)]">
                发送消息
              </h3>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                      姓名
                    </label>
                    <input
                      type="text"
                      required
                      className="w-full px-4 py-3 bg-[var(--bg-elevated)] border border-[var(--border)] rounded-xl text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none transition-colors"
                      placeholder="你的名字"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                      邮箱
                    </label>
                    <input
                      type="email"
                      required
                      className="w-full px-4 py-3 bg-[var(--bg-elevated)] border border-[var(--border)] rounded-xl text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none transition-colors"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    主题
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 bg-[var(--bg-elevated)] border border-[var(--border)] rounded-xl text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none transition-colors"
                    placeholder="项目合作"
                  />
                </div>

                <div>
                  <label className="block text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    消息
                  </label>
                  <textarea
                    required
                    rows={4}
                    className="w-full px-4 py-3 bg-[var(--bg-elevated)] border border-[var(--border)] rounded-xl text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none transition-colors resize-none"
                    placeholder="描述你的项目需求..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={formState === 'sending'}
                  className="btn btn-primary w-full justify-center"
                >
                  {formState === 'idle' && <><Send size={18} /> 发送消息</>}
                  {formState === 'sending' && '发送中...'}
                  {formState === 'sent' && <><CheckCircle size={18} /> 已发送</>}
                </button>
              </form>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
