// ========== 阶段1: 页面加载完成后的初始化 ==========
document.addEventListener('DOMContentLoaded', function() {
    // 初始化加载动画
    initLoader();
    
    // 初始化导航栏
    initNavbar();
    
    // 初始化打字效果
    initTypingEffect();
    
    // 初始化技能进度条
    initSkillBars();
    
    // 初始化项目筛选
    initProjectFilter();
    
    // 初始化联系表单
    initContactForm();
    
    // 初始化返回顶部按钮
    initBackToTop();
    
    // 初始化数字统计动画
    initCountUp();
    
    // 初始化滚动动画
    initScrollAnimations();
});

// ========== 阶段2: 页面加载动画 ==========
function initLoader() {
    const loader = document.getElementById('loader');
    
    // 模拟加载时间（实际使用中可以根据资源加载情况调整）
    setTimeout(() => {
        loader.classList.add('hidden');
        
        // 加载完成后移除loader元素
        setTimeout(() => {
            loader.remove();
        }, 500);
    }, 1500);
}

// ========== 阶段3: 导航栏功能 ==========
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.querySelector('.nav-links');
    const navLinkItems = document.querySelectorAll('.nav-link');

    // 移动端菜单切换
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            menuToggle.querySelector('i').classList.toggle('fa-bars');
            menuToggle.querySelector('i').classList.toggle('fa-times');
        });
    }

    // 点击导航链接关闭移动菜单
    navLinkItems.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                navLinks.classList.remove('active');
                menuToggle.querySelector('i').classList.add('fa-bars');
                menuToggle.querySelector('i').classList.remove('fa-times');
            }
        });
    });

    // 滚动时改变导航栏样式（使用节流优化性能）
    window.addEventListener('scroll', throttle(() => {
        if (window.scrollY > 50) {
            navbar.style.padding = '10px 0';
            navbar.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.padding = '20px 0';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        }
    }, 100));

    // 高亮当前滚动区域的导航链接
    highlightActiveSection();
}

// ========== 阶段4: 高亮当前区域 ==========
function highlightActiveSection() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    window.addEventListener('scroll', throttle(() => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            if (window.scrollY >= sectionTop - 200) {
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

// ========== 阶段5: 打字效果 ==========
function initTypingEffect() {
    const typingElement = document.getElementById('typingText');
    if (!typingElement) return;
    
    const words = ['Web 开发者', 'UI 设计师', '问题解决者', '终身学习者'];
    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typeSpeed = 100;
    
    function type() {
        const currentWord = words[wordIndex];
        
        if (isDeleting) {
            typingElement.textContent = currentWord.substring(0, charIndex - 1);
            charIndex--;
            typeSpeed = 50;
        } else {
            typingElement.textContent = currentWord.substring(0, charIndex + 1);
            charIndex++;
            typeSpeed = 100;
        }
        
        if (!isDeleting && charIndex === currentWord.length) {
            // 完成打字，暂停后开始删除
            typeSpeed = 2000;
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            // 完成删除，切换到下一个单词
            isDeleting = false;
            wordIndex = (wordIndex + 1) % words.length;
            typeSpeed = 500;
        }
        
        setTimeout(type, typeSpeed);
    }
    
    // 开始打字效果
    setTimeout(type, 1000);
}

// ========== 阶段6: 技能进度条动画 ==========
function initSkillBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    // 使用Intersection Observer API检测元素是否进入视口
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.getAttribute('data-width');
                
                // 添加动画效果
                setTimeout(() => {
                    bar.style.width = `${width}%`;
                }, 300);
                
                // 一旦触发就停止观察
                observer.unobserve(bar);
            }
        });
    }, {
        threshold: 0.5 // 当元素50%进入视口时触发
    });
    
    progressBars.forEach(bar => {
        observer.observe(bar);
    });
}

// ========== 阶段7: 项目筛选功能 ==========
function initProjectFilter() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const projectCards = document.querySelectorAll('.project-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有按钮的active类
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // 给当前按钮添加active类
            button.classList.add('active');
            
            const filterValue = button.getAttribute('data-filter');
            
            // 筛选项目卡片
            projectCards.forEach(card => {
                if (filterValue === 'all' || card.getAttribute('data-category') === filterValue) {
                    card.style.display = 'block';
                    // 添加淡入动画
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 50);
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// ========== 阶段8: 联系表单处理 ==========
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const formData = new FormData(this);
            const submitButton = this.querySelector('button[type="submit"]');
            
            // 禁用提交按钮，显示加载状态
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';
            
            // 模拟表单提交（实际使用中需要替换为真实的API调用）
            setTimeout(() => {
                // 显示成功消息
                alert('消息已发送！感谢你的联系。');
                
                // 重置表单
                contactForm.reset();
                
                // 恢复提交按钮
                submitButton.disabled = false;
                submitButton.innerHTML = '发送消息 <i class="fas fa-paper-plane"></i>';
            }, 2000);
        });
    }
}

// ========== 阶段9: 返回顶部按钮 ==========
function initBackToTop() {
    const backToTopButton = document.getElementById('backToTop');

    window.addEventListener('scroll', throttle(() => {
        // 当滚动超过500px时显示按钮
        if (window.scrollY > 500) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    }, 100));

    backToTopButton.addEventListener('click', () => {
        // 平滑滚动到顶部
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ========== 阶段10: 数字统计动画 ==========
function initCountUp() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const target = parseInt(element.getAttribute('data-count'));
                
                // 开始计数动画
                countUp(element, target);
                
                // 一旦触发就停止观察
                observer.unobserve(element);
            }
        });
    }, {
        threshold: 0.5
    });
    
    statNumbers.forEach(number => {
        observer.observe(number);
    });
}

function countUp(element, target) {
    let current = 0;
    const increment = target / 50; // 分50步完成
    
    const timer = setInterval(() => {
        current += increment;
        
        if (current >= target) {
            clearInterval(timer);
            current = target;
        }
        
        element.textContent = Math.floor(current);
    }, 30);
}

// ========== 阶段11: 滚动动画 ==========
function initScrollAnimations() {
    // 为需要动画的元素添加类
    const animatedElements = document.querySelectorAll(
        '.skill-card, .project-card, .contact-item, .stat-item'
    );
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // 一旦触发就停止观察
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        // 初始状态
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        // 开始观察
        observer.observe(element);
    });
}

// ========== 阶段12: 工具函数 ==========
// 节流函数，用于优化scroll事件
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 防抖函数，用于resize事件
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}
