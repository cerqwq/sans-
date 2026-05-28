'use client';

import { Code, Heart } from 'lucide-react';

const links = [
  { label: '首页', href: '#home' },
  { label: '关于', href: '#about' },
  { label: '技能', href: '#skills' },
  { label: '项目', href: '#projects' },
  { label: '联系', href: '#contact' },
];

export default function Footer() {
  const scrollTo = (href: string) => {
    const el = document.querySelector(href);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <footer className="py-12 border-t border-[var(--border)]">
      <div className="max-w-[var(--container-max)] mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
          {/* Logo */}
          <div className="flex items-center gap-3 justify-center md:justify-start">
            <span className="w-10 h-10 bg-[var(--accent)] text-[var(--bg-primary)] font-['var(--font-noto)'] text-xl rounded-[10px] flex items-center justify-center">
              宿
            </span>
            <span className="font-['var(--font-mono)'] text-sm font-bold tracking-[3px]">
              LISU
            </span>
          </div>

          {/* Links */}
          <ul className="flex justify-center gap-6">
            {links.map(link => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={(e) => { e.preventDefault(); scrollTo(link.href); }}
                  className="text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>

          {/* Social */}
          <div className="flex justify-center md:justify-end gap-4">
            <a
              href="https://github.com/cerqwq/sans-"
              target="_blank"
              rel="noopener noreferrer"
              className="w-10 h-10 rounded-xl bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:border-[var(--accent)] transition-all"
            >
              <Code size={18} />
            </a>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-[var(--border)] text-center">
          <p className="text-xs text-[var(--text-muted)]">
            © {new Date().getFullYear()} 李宿. All rights reserved.
          </p>
          <p className="text-xs text-[var(--text-muted)] mt-2 flex items-center justify-center gap-1">
            Made with <Heart size={12} className="text-[var(--accent)]" /> using Next.js
          </p>
        </div>
      </div>
    </footer>
  );
}
