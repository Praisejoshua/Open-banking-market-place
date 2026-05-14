/**
 * Open Banking Marketplace - Main JavaScript
 * Design and Implementation by ILOEGBUNAM VALERIAN CHIMDINDU
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            const icon = this.querySelector('i');
            if (sidebar.classList.contains('collapsed')) {
                icon.classList.remove('fa-chevron-left');
                icon.classList.add('fa-chevron-right');
            } else {
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-left');
            }
        });
    }
    
    // Mobile Menu
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.add('active');
            if (sidebarOverlay) sidebarOverlay.style.display = 'block';
        });
    }
    
    if (sidebarOverlay && sidebar) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            this.style.display = 'none';
        });
    }
    
    // Dropdowns
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(function(dropdown) {
        const btn = dropdown.querySelector('button');
        if (btn) {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                // Close other dropdowns
                dropdowns.forEach(function(d) {
                    if (d !== dropdown) d.classList.remove('active');
                });
                dropdown.classList.toggle('active');
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        dropdowns.forEach(function(dropdown) {
            dropdown.classList.remove('active');
        });
    });
    
    // Role Selection (Registration)
    const roleCards = document.querySelectorAll('.role-card');
    
    roleCards.forEach(function(card) {
        card.addEventListener('click', function() {
            roleCards.forEach(function(c) {
                c.classList.remove('selected');
            });
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert-dismissible');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Mobile menu toggle (landing)
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const landingNav = document.querySelector('.landing-nav');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const navLinks = document.querySelector('.nav-links');
            const navAuth = document.querySelector('.nav-auth');
            if (navLinks) navLinks.classList.toggle('active');
            if (navAuth) navAuth.classList.toggle('active');
        });
    }
});

// Toggle Password Visibility
function togglePassword(btn) {
    const input = btn.parentElement.querySelector('input');
    const icon = btn.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// AJAX helper
function ajaxRequest(url, method, data, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    if (method === 'POST') {
        xhr.setRequestHeader('X-CSRFToken', getCsrfToken());
    }
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    callback(null, response);
                } catch (e) {
                    callback(null, xhr.responseText);
                }
            } else {
                callback(new Error('Request failed'), null);
            }
        }
    };
    
    if (data) {
        xhr.send(data);
    } else {
        xhr.send();
    }
}

function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookieValue ? cookieValue.split('=')[1] : '';
}

// Loan Calculator
function calculateLoan() {
    const amount = document.getElementById('calc-amount').value;
    const rate = document.getElementById('calc-rate').value;
    const months = document.getElementById('calc-months').value;
    
    if (amount && rate && months) {
        const formData = new FormData();
        formData.append('amount', amount);
        formData.append('rate', rate);
        formData.append('months', months);
        
        ajaxRequest('/loans/ajax/calculate/', 'POST', formData, function(err, response) {
            if (!err && response.success) {
                document.getElementById('calc-monthly').textContent = 'N' + parseFloat(response.monthly_payment).toLocaleString('en-NG', {minimumFractionDigits: 2});
                document.getElementById('calc-total').textContent = 'N' + parseFloat(response.total_repayment).toLocaleString('en-NG', {minimumFractionDigits: 2});
                document.getElementById('calc-interest').textContent = 'N' + parseFloat(response.total_interest).toLocaleString('en-NG', {minimumFractionDigits: 2});
            }
        });
    }
}

// Credit Score Animation
function animateCreditScore() {
    const rings = document.querySelectorAll('.score-ring-fill');
    
    rings.forEach(function(ring) {
        const targetOffset = ring.getAttribute('data-target');
        if (targetOffset) {
            setTimeout(function() {
                ring.style.strokeDashoffset = targetOffset;
            }, 300);
        }
    });
}

// Tab switching
function switchTab(tabId) {
    // Hide all tab panels
    document.querySelectorAll('.tab-panel').forEach(function(panel) {
        panel.style.display = 'none';
    });
    
    // Show selected panel
    const selectedPanel = document.getElementById(tabId);
    if (selectedPanel) {
        selectedPanel.style.display = 'block';
    }
    
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(function(tab) {
        tab.classList.remove('active');
        if (tab.getAttribute('data-tab') === tabId) {
            tab.classList.add('active');
        }
    });
}
