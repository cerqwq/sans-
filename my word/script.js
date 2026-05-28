// =============================================
// PORTFOLIO — Interactive Features
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    initLoader();
    initCursor();
    initNavbar();
    initMobileMenu();
    initTypingEffect();
    initSkillBars();
    initProjectFilter();
    initContactForm();
    initBackToTop();
    initCountUp();
    initSmoothScroll();
    initThemeToggle();
    initProjectModal();
    initMagneticButtons();
    initTiltCards();

    // GSAP 动画系统
    if (typeof gsap !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
        initGSAPAnimations();
    } else {
        // Fallback: 使用原生 scroll reveal
        initScrollReveal();
        initParallax();
    }
});

// =============================================
// LOADER
// =============================================
function initLoader() {
    const loader = document.getElementById('loader');
    if (!loader) return;
    window.addEventListener('load', () => {
        setTimeout(() => {
            loader.classList.add('hidden');
            setTimeout(() => loader.remove(), 600);
        }, 800);
    });
}

// =============================================
// CUSTOM CURSOR
// =============================================
function initCursor() {
    const dot = document.getElementById('cursorDot');
    const ring = document.getElementById('cursorRing');
    if (!dot || !ring) return;

    // Hide on touch devices
    if ('ontouchstart' in window) {
        dot.style.display = 'none';
        ring.style.display = 'none';
        return;
    }

    let mouseX = 0, mouseY = 0;
    let ringX = 0, ringY = 0;
    let animFrameId = null;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        dot.style.left = mouseX + 'px';
        dot.style.top = mouseY + 'px';
    });

    // Smooth ring follow — only animate when mouse has moved
    function animateRing() {
        ringX += (mouseX - ringX) * 0.15;
        ringY += (mouseY - ringY) * 0.15;
        ring.style.left = ringX + 'px';
        ring.style.top = ringY + 'px';
        animFrameId = requestAnimationFrame(animateRing);
    }
    animateRing();

    // Hover effect on interactive elements
    const hoverTargets = document.querySelectorAll('a, button, .project-card, .skill-card, .filter-btn');
    hoverTargets.forEach(el => {
        el.addEventListener('mouseenter', () => {
            dot.classList.add('hover');
            ring.classList.add('hover');
        });
        el.addEventListener('mouseleave', () => {
            dot.classList.remove('hover');
            ring.classList.remove('hover');
        });
    });
}

// =============================================
// NAVBAR
// =============================================
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    let lastScroll = 0;

    window.addEventListener('scroll', throttle(() => {
        const scrollY = window.scrollY;

        if (scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = scrollY;
    }, 50));

    // Active section highlight
    highlightActiveSection();
}

function highlightActiveSection() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

    window.addEventListener('scroll', throttle(() => {
        let current = '';
        const scrollY = window.scrollY + 200;

        sections.forEach(section => {
            if (scrollY >= section.offsetTop) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }, 100));
}

// =============================================
// MOBILE MENU
// =============================================
function initMobileMenu() {
    const toggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');
    if (!toggle || !navLinks) return;

    toggle.setAttribute('aria-expanded', 'false');

    toggle.addEventListener('click', () => {
        const isOpen = toggle.classList.toggle('active');
        navLinks.classList.toggle('active');
        toggle.setAttribute('aria-expanded', String(isOpen));
        document.body.style.overflow = isOpen ? 'hidden' : '';

        // Staggered animation for nav links
        if (isOpen) {
            const links = navLinks.querySelectorAll('.nav-link');
            links.forEach((link, i) => {
                link.style.opacity = '0';
                link.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    link.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                    link.style.opacity = '1';
                    link.style.transform = 'translateY(0)';
                }, 100 + i * 80);
            });
        } else {
            // Reset styles on close
            const links = navLinks.querySelectorAll('.nav-link');
            links.forEach(link => {
                link.style.opacity = '';
                link.style.transform = '';
                link.style.transition = '';
            });
        }
    });

    // Close on link click
    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            toggle.classList.remove('active');
            toggle.setAttribute('aria-expanded', 'false');
            navLinks.classList.remove('active');
            document.body.style.overflow = '';
            // Reset link styles
            navLinks.querySelectorAll('.nav-link').forEach(l => {
                l.style.opacity = '';
                l.style.transform = '';
                l.style.transition = '';
            });
        });
    });
}

// =============================================
// TYPING EFFECT
// =============================================
function initTypingEffect() {
    const el = document.getElementById('typingText');
    if (!el) return;

    const words = ['Web 开发者', 'UI 设计师', '问题解决者', '终身学习者'];
    let wordIdx = 0;
    let charIdx = 0;
    let deleting = false;
    let speed = 100;

    function type() {
        const word = words[wordIdx];

        if (deleting) {
            el.textContent = word.substring(0, charIdx - 1);
            charIdx--;
            speed = 40;
        } else {
            el.textContent = word.substring(0, charIdx + 1);
            charIdx++;
            speed = 80;
        }

        if (!deleting && charIdx === word.length) {
            speed = 2500;
            deleting = true;
        } else if (deleting && charIdx === 0) {
            deleting = false;
            wordIdx = (wordIdx + 1) % words.length;
            speed = 400;
        }

        setTimeout(type, speed);
    }

    setTimeout(type, 1200);
}

// =============================================
// SKILL BARS
// =============================================
function initSkillBars() {
    const bars = document.querySelectorAll('.skill-bar-fill');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.getAttribute('data-width');
                setTimeout(() => {
                    bar.style.width = width + '%';
                }, 200);
                observer.unobserve(bar);
            }
        });
    }, { threshold: 0.3 });

    bars.forEach(bar => observer.observe(bar));
}

// =============================================
// PROJECT FILTER
// =============================================
function initProjectFilter() {
    const buttons = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.project-card');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');

            const filter = btn.getAttribute('data-filter');

            cards.forEach((card, i) => {
                const category = card.getAttribute('data-category');
                const show = filter === 'all' || category === filter;

                if (show) {
                    card.style.display = '';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';

                    setTimeout(() => {
                        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, i * 80);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

// =============================================
// CONTACT FORM
// =============================================
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const btn = form.querySelector('button[type="submit"]');
        const originalHTML = btn.innerHTML;

        // 获取表单数据 using IDs
        const name = document.getElementById('contactName')?.value || '';
        const email = document.getElementById('contactEmail')?.value || '';
        const subject = document.getElementById('contactSubject')?.value || '';
        const message = document.getElementById('contactMessage')?.value || '';

        // 验证表单
        if (!name || !email || !message) {
            alert('请填写所有必填字段');
            return;
        }

        // 邮箱格式验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('请输入有效的邮箱地址');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>发送中...</span>';

        // 这里需要后端API支持
        // 目前使用 mailto: 作为临时解决方案
        const mailtoLink = `mailto:995935899@qq.com?subject=${encodeURIComponent(subject || '来自网站的留言')}&body=${encodeURIComponent(`姓名: ${name}\n邮箱: ${email}\n\n${message}`)}`;

        setTimeout(() => {
            try {
                // 尝试打开邮件客户端
                window.location.href = mailtoLink;
                alert('感谢你的联系！已打开邮件客户端，请发送邮件。');
            } catch (err) {
                console.error('Failed to open mail client:', err);
                alert('无法打开邮件客户端，请手动发送邮件至 995935899@qq.com');
            } finally {
                form.reset();
                btn.disabled = false;
                btn.innerHTML = originalHTML;
            }
        }, 1000);
    });
}

// =============================================
// BACK TO TOP
// =============================================
function initBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;

    window.addEventListener('scroll', throttle(() => {
        btn.classList.toggle('visible', window.scrollY > 500);
    }, 100));

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// =============================================
// COUNT UP
// =============================================
function initCountUp() {
    const numbers = document.querySelectorAll('.stat-num');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                countUp(entry.target, parseInt(entry.target.getAttribute('data-count')));
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    numbers.forEach(n => observer.observe(n));
}

function countUp(el, target) {
    let current = 0;
    const step = target / 60;
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = Math.floor(current);
    }, 25);
}

// =============================================
// SCROLL REVEAL
// =============================================
function initScrollReveal() {
    const elements = document.querySelectorAll(
        '.skill-card, .project-card, .contact-item, .highlight-item, .section-header, .about-content, .about-visual, .contact-info, .contact-form-wrap'
    );

    elements.forEach(el => el.classList.add('reveal'));

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                // Stagger delay based on sibling index
                const parent = entry.target.parentElement;
                const siblings = [...parent.children].filter(c => c.classList.contains('reveal'));
                const idx = siblings.indexOf(entry.target);

                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, idx * 100);

                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
}

// =============================================
// SMOOTH SCROLL
// =============================================
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                e.preventDefault();
                const offset = 80;
                const top = target.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: 'smooth' });
            }
        });
    });
}

// =============================================
// THEME TOGGLE
// =============================================
function initThemeToggle() {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    // Check localStorage first, then system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'light' || (!savedTheme && !systemPrefersDark)) {
        document.documentElement.classList.add('light-theme');
    }

    toggle.addEventListener('click', () => {
        document.documentElement.classList.add('theme-transitioning');
        document.documentElement.classList.toggle('light-theme');
        const isLight = document.documentElement.classList.contains('light-theme');
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
        setTimeout(() => {
            document.documentElement.classList.remove('theme-transitioning');
        }, 400);
    });

    // Listen for system preference changes (only if no manual override)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            document.documentElement.classList.toggle('light-theme', !e.matches);
        }
    });
}

// =============================================
// PARALLAX
// =============================================
function initParallax() {
    // Skip if user prefers reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const heroSection = document.querySelector('.hero-section');
    if (!heroSection) return;

    const glows = heroSection.querySelectorAll('.hero-glow-1, .hero-glow-2');
    const gridLines = heroSection.querySelector('.hero-grid-lines');

    window.addEventListener('scroll', throttle(() => {
        const scrollY = window.scrollY;
        const heroHeight = heroSection.offsetHeight;

        if (scrollY > heroHeight) return;

        glows.forEach((glow, i) => {
            const speed = i === 0 ? 0.3 : 0.5;
            glow.style.transform = `translateY(${scrollY * speed}px)`;
        });

        if (gridLines) {
            gridLines.style.transform = `translateY(${scrollY * 0.1}px)`;
        }
    }, 16));
}

// =============================================
// PROJECT MODAL
// =============================================
function initProjectModal() {
    const modal = document.getElementById('projectModal');
    const backdrop = document.getElementById('modalBackdrop');
    const closeBtn = document.getElementById('modalClose');
    const detailButtons = document.querySelectorAll('.project-link-detail');

    if (!modal) return;

    // Project features data
    const projectFeatures = {
        '斗地主在线游戏': [
            '支持多人实时在线对战',
            '智能AI对手系统',
            '实时聊天与表情互动',
            '流畅的动画效果',
            '响应式设计，支持移动端'
        ],
        '手势粒子特效': [
            '基于MediaPipe手势识别',
            '支持多种手势控制',
            'Canvas高性能粒子渲染',
            '实时手势反馈',
            '沉浸式交互体验'
        ]
    };

    function openModal(card) {
        const title = card.getAttribute('data-title');
        const desc = card.getAttribute('data-desc');
        const icon = card.getAttribute('data-icon');
        const link = card.getAttribute('data-link');
        const source = card.getAttribute('data-source');
        const linkText = card.getAttribute('data-link-text') || '查看项目';
        const tags = card.querySelectorAll('.project-tags span');

        // Set modal content
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalDesc').textContent = desc;
        document.getElementById('modalPlaceholder').innerHTML = '<i class="' + icon + '"></i>';

        // Set tags
        const tagsContainer = document.getElementById('modalTags');
        tagsContainer.innerHTML = '';
        tags.forEach(tag => {
            const span = document.createElement('span');
            span.textContent = tag.textContent;
            tagsContainer.appendChild(span);
        });

        // Set features
        const featuresContainer = document.getElementById('modalFeatures');
        featuresContainer.innerHTML = '';
        const features = projectFeatures[title] || [];
        features.forEach(feature => {
            const li = document.createElement('li');
            li.textContent = feature;
            featuresContainer.appendChild(li);
        });

        // Set links
        document.getElementById('modalLink').href = link;
        document.getElementById('modalLink').querySelector('span').textContent = linkText;
        document.getElementById('modalSource').href = source;

        // Show modal
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        // Store trigger and focus close button
        modal._trigger = card;
        setTimeout(() => closeBtn.focus(), 100);
    }

    function closeModal() {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';

        // Return focus to trigger
        if (modal._trigger) {
            const detailBtn = modal._trigger.querySelector('.project-link-detail');
            if (detailBtn) detailBtn.focus();
        }
    }

    // Event listeners
    detailButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const card = btn.closest('.project-card');
            openModal(card);
        });
    });

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (backdrop) backdrop.addEventListener('click', closeModal);

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
}

// =============================================
// THROTTLE
// =============================================
function throttle(fn, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            fn.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// =============================================
// MAGNETIC BUTTONS
// =============================================
function initMagneticButtons() {
    const buttons = document.querySelectorAll('.btn-primary, .btn-ghost, .btn-outline');

    buttons.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            btn.style.setProperty('--x', x + 'px');
            btn.style.setProperty('--y', y + 'px');

            // Magnetic effect - slightly pull button towards cursor
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const deltaX = (x - centerX) * 0.15;
            const deltaY = (y - centerY) * 0.15;

            btn.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
        });

        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
        });
    });
}

// =============================================
// TILT CARDS (3D hover effect)
// =============================================
function initTiltCards() {
    const cards = document.querySelectorAll('.skill-card, .project-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;

            card.style.transform = `perspective(800px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) translateY(-4px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            card.style.transition = 'transform 0.5s ease';
            setTimeout(() => {
                card.style.transition = '';
            }, 500);
        });
    });
}

// =============================================
// GSAP 动画系统 (专业级)
// =============================================
function initGSAPAnimations() {
    // Skip if user prefers reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    // Hero 入场动画时间线
    const heroTl = gsap.timeline({ delay: 0.8 });

    heroTl
        .from('.hero-tag', {
            opacity: 0,
            y: 30,
            duration: 0.8,
            ease: 'power3.out'
        })
        .from('.title-line-1', {
            opacity: 0,
            y: 40,
            duration: 0.7,
            ease: 'power3.out'
        }, '-=0.4')
        .from('.title-line-2', {
            opacity: 0,
            y: 50,
            duration: 0.8,
            ease: 'power3.out'
        }, '-=0.3')
        .from('.title-line-3', {
            opacity: 0,
            y: 30,
            duration: 0.7,
            ease: 'power3.out'
        }, '-=0.3')
        .from('.hero-desc', {
            opacity: 0,
            y: 30,
            duration: 0.7,
            ease: 'power3.out'
        }, '-=0.3')
        .from('.hero-actions .btn', {
            opacity: 0,
            y: 20,
            stagger: 0.15,
            duration: 0.6,
            ease: 'power3.out'
        }, '-=0.3')
        .from('.hero-stats .hero-stat', {
            opacity: 0,
            y: 20,
            stagger: 0.1,
            duration: 0.6,
            ease: 'power3.out'
        }, '-=0.3')
        .from('.hero-right', {
            opacity: 0,
            x: 60,
            duration: 1,
            ease: 'power3.out'
        }, '-=0.8');

    // ScrollTrigger - Hero 视差效果
    gsap.to('.hero-glow-1', {
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: 1
        },
        y: -150,
        opacity: 0.02
    });

    gsap.to('.hero-glow-2', {
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: 1
        },
        y: -100,
        opacity: 0.02
    });

    gsap.to('.hero-grid-lines', {
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: 1
        },
        y: -50,
        opacity: 0
    });

    // ScrollTrigger - 区块标题入场
    gsap.utils.toArray('.section-header').forEach(header => {
        gsap.from(header, {
            scrollTrigger: {
                trigger: header,
                start: 'top 85%',
                end: 'top 60%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            y: 60,
            duration: 1,
            ease: 'power3.out'
        });
    });

    // ScrollTrigger - 技能卡片交错入场
    gsap.utils.toArray('.skill-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            y: 60,
            rotation: -2,
            duration: 0.8,
            delay: i * 0.1,
            ease: 'power3.out'
        });
    });

    // ScrollTrigger - 项目卡片交错入场
    gsap.utils.toArray('.project-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            y: 80,
            scale: 0.95,
            duration: 0.9,
            delay: i * 0.15,
            ease: 'power3.out'
        });
    });

    // ScrollTrigger - 技能进度条动画
    gsap.utils.toArray('.skill-bar-fill').forEach(bar => {
        const width = bar.getAttribute('data-width');
        gsap.to(bar, {
            scrollTrigger: {
                trigger: bar,
                start: 'top 90%',
                toggleActions: 'play none none reverse'
            },
            width: width + '%',
            duration: 1.5,
            ease: 'power2.out'
        });
    });

    // ScrollTrigger - 统计数字计数动画
    gsap.utils.toArray('.stat-num').forEach(num => {
        const target = parseInt(num.getAttribute('data-count'));
        const obj = { value: 0 };

        gsap.to(obj, {
            scrollTrigger: {
                trigger: num,
                start: 'top 90%',
                toggleActions: 'play none none reverse'
            },
            value: target,
            duration: 2,
            ease: 'power2.out',
            onUpdate: () => {
                num.textContent = Math.floor(obj.value);
            }
        });
    });

    // ScrollTrigger - 联系区域入场
    gsap.from('.contact-info', {
        scrollTrigger: {
            trigger: '.contact-section',
            start: 'top 80%',
            toggleActions: 'play none none reverse'
        },
        opacity: 0,
        x: -60,
        duration: 1,
        ease: 'power3.out'
    });

    gsap.from('.contact-form-wrap', {
        scrollTrigger: {
            trigger: '.contact-section',
            start: 'top 80%',
            toggleActions: 'play none none reverse'
        },
        opacity: 0,
        x: 60,
        duration: 1,
        ease: 'power3.out'
    });

    // ScrollTrigger - Footer 入场
    gsap.from('.footer-top', {
        scrollTrigger: {
            trigger: '.footer',
            start: 'top 90%',
            toggleActions: 'play none none reverse'
        },
        opacity: 0,
        y: 40,
        duration: 0.8,
        ease: 'power3.out'
    });

    // 返回顶部按钮显示/隐藏
    ScrollTrigger.create({
        trigger: 'body',
        start: 'top -500px',
        onEnter: () => document.getElementById('backToTop')?.classList.add('visible'),
        onLeaveBack: () => document.getElementById('backToTop')?.classList.remove('visible')
    });
}
