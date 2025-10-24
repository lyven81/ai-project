// Stock Analysis Agent - Frontend Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Animated chart bars on scroll
    const observerOptions = {
        threshold: 0.3,
        rootMargin: '0px 0px -100px 0px'
    };

    const chartObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bars = entry.target.querySelectorAll('.chart-bar');
                bars.forEach((bar, index) => {
                    setTimeout(() => {
                        bar.style.opacity = '0';
                        bar.style.transform = 'translateY(20px)';

                        setTimeout(() => {
                            bar.style.transition = 'all 0.6s ease-out';
                            bar.style.opacity = '1';
                            bar.style.transform = 'translateY(0)';
                        }, 50);
                    }, index * 100);
                });

                chartObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const chartPreviews = document.querySelectorAll('.chart-preview');
    chartPreviews.forEach(chart => {
        chartObserver.observe(chart);
    });

    // Card hover effects
    const cards = document.querySelectorAll('.overview-card, .feature-card, .usage-card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });

    // Workflow steps animation
    const workflowObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const steps = entry.target.querySelectorAll('.workflow-step');
                steps.forEach((step, index) => {
                    setTimeout(() => {
                        step.style.opacity = '0';
                        step.style.transform = 'translateX(-30px)';

                        setTimeout(() => {
                            step.style.transition = 'all 0.5s ease-out';
                            step.style.opacity = '1';
                            step.style.transform = 'translateX(0)';
                        }, 50);
                    }, index * 200);
                });

                workflowObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const workflows = document.querySelectorAll('.workflow');
    workflows.forEach(workflow => {
        workflowObserver.observe(workflow);
    });

    // Add active state to navigation based on scroll position
    const sections = document.querySelectorAll('section[id]');

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            if (window.pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });

    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
        }
    });

    // Copy code to clipboard functionality
    const codeBlocks = document.querySelectorAll('.code-block');

    codeBlocks.forEach(block => {
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            Copy
        `;

        // Style the copy button
        copyButton.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.75rem;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.3s ease;
        `;

        // Make code block relative for absolute positioning
        block.style.position = 'relative';
        block.appendChild(copyButton);

        // Copy functionality
        copyButton.addEventListener('click', () => {
            const code = block.querySelector('code').textContent;
            navigator.clipboard.writeText(code).then(() => {
                copyButton.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    Copied!
                `;
                copyButton.style.background = 'rgba(16, 185, 129, 0.2)';

                setTimeout(() => {
                    copyButton.innerHTML = `
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        Copy
                    `;
                    copyButton.style.background = 'rgba(255, 255, 255, 0.1)';
                }, 2000);
            });
        });

        copyButton.addEventListener('mouseenter', () => {
            copyButton.style.background = 'rgba(255, 255, 255, 0.2)';
        });

        copyButton.addEventListener('mouseleave', () => {
            copyButton.style.background = 'rgba(255, 255, 255, 0.1)';
        });
    });

    // Animate score card on scroll
    const scoreCardObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const scoreValue = entry.target.querySelector('.score-value');
                if (scoreValue) {
                    const targetScore = parseInt(scoreValue.textContent);
                    let currentScore = 0;
                    const increment = targetScore / 50;

                    const timer = setInterval(() => {
                        currentScore += increment;
                        if (currentScore >= targetScore) {
                            currentScore = targetScore;
                            clearInterval(timer);
                        }
                        scoreValue.textContent = Math.floor(currentScore) + '/100';
                    }, 20);
                }

                scoreCardObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const scoreCards = document.querySelectorAll('.score-card');
    scoreCards.forEach(card => {
        scoreCardObserver.observe(card);
    });

    // Add tooltips to chart bars
    const chartBars = document.querySelectorAll('.chart-bar');

    chartBars.forEach(bar => {
        bar.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
    });

    // Feature card expand on click (mobile)
    if (window.innerWidth <= 768) {
        const featureCards = document.querySelectorAll('.feature-card');

        featureCards.forEach(card => {
            const content = card.querySelector('.feature-content');
            const header = card.querySelector('.feature-header');

            if (content && header) {
                content.style.maxHeight = '0';
                content.style.overflow = 'hidden';
                content.style.transition = 'max-height 0.3s ease';

                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    if (content.style.maxHeight === '0px' || content.style.maxHeight === '') {
                        content.style.maxHeight = content.scrollHeight + 'px';
                    } else {
                        content.style.maxHeight = '0';
                    }
                });
            }
        });
    }

    // Add loading animation for external links
    const externalLinks = document.querySelectorAll('a[target="_blank"]');

    externalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Visual feedback
            this.style.opacity = '0.7';
            setTimeout(() => {
                this.style.opacity = '1';
            }, 200);
        });
    });

    // Table row highlighting
    const tableRows = document.querySelectorAll('.criteria-table tbody tr');

    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            tableRows.forEach(r => r.style.background = '');
            this.style.background = 'rgba(30, 64, 175, 0.05)';
        });
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', () => {
        const hero = document.querySelector('.hero');
        if (hero) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.5;
            hero.style.transform = `translate3d(0, ${rate}px, 0)`;
        }
    });

    console.log('Stock Analysis Agent - Frontend loaded successfully');
});

// Utility function for number formatting
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Utility function for percentage formatting
function formatPercentage(num) {
    return (num * 100).toFixed(2) + '%';
}

// Export functions for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatNumber,
        formatPercentage
    };
}
