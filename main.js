/**
 * TalentBeacon™ – Main JavaScript
 * Core utilities: auth, API, toast, nav, sidebar
 */

/* ── Token Management ─────────────────────────────────── */
const Auth = {
  getToken() { return localStorage.getItem('tb_token'); },
  setToken(t) { localStorage.setItem('tb_token', t); },
  getUser()  { 
    try { return JSON.parse(localStorage.getItem('tb_user') || 'null'); } 
    catch { return null; }
  },
  setUser(u) { localStorage.setItem('tb_user', JSON.stringify(u)); },
  clear()    { localStorage.removeItem('tb_token'); localStorage.removeItem('tb_user'); },
  isLoggedIn(){ return !!this.getToken(); },
  getRole()  { const u = this.getUser(); return u ? u.role : null; },
  getEmployeeId() { const u = this.getUser(); return u ? u.employee_id : null; },
};

/* ── API Client ─────────────────────────────────────────── */
const API = {
  BASE: '/api',

  async request(method, path, body = null, options = {}) {
    const token = Auth.getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const config = { method, headers, ...options };
    if (body) config.body = JSON.stringify(body);

    try {
      const res = await fetch(`${this.BASE}${path}`, config);

      // Handle 401 - redirect to login
      if (res.status === 401) {
        Auth.clear();
        window.location.href = '/login';
        return null;
      }

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      return data;
    } catch (err) {
      throw err;
    }
  },

  get(path)         { return this.request('GET', path); },
  post(path, body)  { return this.request('POST', path, body); },
  put(path, body)   { return this.request('PUT', path, body); },
  delete(path)      { return this.request('DELETE', path); },
};

/* ── Toast Notifications ─────────────────────────────────── */
const Toast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', duration = 4000) {
    this.init();
    const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span style="font-size:16px;color:var(--${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'})">${icons[type] || 'ℹ'}</span>
      <span>${message}</span>
    `;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  success(msg) { this.show(msg, 'success'); },
  error(msg)   { this.show(msg, 'error'); },
  info(msg)    { this.show(msg, 'info'); },
  warning(msg) { this.show(msg, 'warning'); },
};

/* ── Sidebar Navigation ─────────────────────────────────── */
const Sidebar = {
  init() {
    this.setActiveItem();
    this.renderUserProfile();
    this.setupNavigation();
  },

  setActiveItem() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item[data-href]').forEach(el => {
      if (path.includes(el.dataset.href)) {
        el.classList.add('active');
      }
    });
  },

  renderUserProfile() {
    const user = Auth.getUser();
    if (!user) return;

    const nameEl = document.getElementById('sidebar-user-name');
    const roleEl = document.getElementById('sidebar-user-role');
    const avatarEl = document.getElementById('sidebar-avatar');

    if (nameEl) nameEl.textContent = user.employee?.name || user.email.split('@')[0];
    if (roleEl) roleEl.textContent = user.role;
    if (avatarEl) {
      const name = user.employee?.name || user.email;
      avatarEl.textContent = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
      avatarEl.style.background = roleColors[user.role] || 'linear-gradient(135deg, #6366F1, #8B5CF6)';
    }
  },

  setupNavigation() {
    document.querySelectorAll('.nav-item[data-href]').forEach(el => {
      el.addEventListener('click', () => {
        window.location.href = el.dataset.href;
      });
    });
  },
};

const roleColors = {
  admin:    'linear-gradient(135deg, #EF4444, #F97316)',
  manager:  'linear-gradient(135deg, #6366F1, #8B5CF6)',
  employee: 'linear-gradient(135deg, #06B6D4, #3B82F6)',
};

/* ── Auth Guard ─────────────────────────────────────────── */
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = '/login';
    return false;
  }
  return true;
}

function requireRole(...roles) {
  if (!requireAuth()) return false;
  const role = Auth.getRole();
  if (!roles.includes(role)) {
    Toast.error('You do not have permission to access this page.');
    setTimeout(() => {
      const role = Auth.getRole();
      if (role === 'admin') window.location.href = '/admin/dashboard';
      else if (role === 'manager') window.location.href = '/manager/talent-discovery';
      else window.location.href = '/employee/career-dashboard';
    }, 1500);
    return false;
  }
  return true;
}

/* ── Logout ─────────────────────────────────────────────── */
async function logout() {
  try {
    await API.post('/auth/logout');
  } catch (e) {}
  Auth.clear();
  window.location.href = '/login';
}

/* ── Number Formatting ─────────────────────────────────── */
function animateNumber(el, target, duration = 1000) {
  let start = 0;
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    el.textContent = Math.round(eased * target);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ── Score Color Helper ─────────────────────────────────── */
function scoreClass(score) {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  if (score >= 40) return 'fair';
  return 'poor';
}

function scoreColor(score) {
  if (score >= 80) return '#10B981';
  if (score >= 60) return '#3B82F6';
  if (score >= 40) return '#F59E0B';
  return '#EF4444';
}

/* ── SVG Score Ring ─────────────────────────────────────── */
function createScoreRing(containerId, score, size = 90) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const color = scoreColor(score);

  container.innerHTML = `
    <div class="score-ring-container" style="width:${size}px;height:${size}px">
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle cx="${size/2}" cy="${size/2}" r="${radius}" 
          fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
        <circle cx="${size/2}" cy="${size/2}" r="${radius}"
          fill="none" stroke="${color}" stroke-width="8"
          stroke-linecap="round"
          stroke-dasharray="${circumference}"
          stroke-dashoffset="${circumference * (1 - score / 100)}"
          transform="rotate(-90 ${size/2} ${size/2})"
          style="transition: stroke-dashoffset 1.5s cubic-bezier(0.4,0,0.2,1)"/>
      </svg>
      <span class="score-ring-value" style="color:${color}">${Math.round(score)}%</span>
    </div>`;
}

/* ── Loading State Helpers ─────────────────────────────── */
function showLoading(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const overlay = document.createElement('div');
  overlay.className = 'loading-overlay';
  overlay.id = `loading-${containerId}`;
  overlay.innerHTML = '<div class="spinner"></div>';
  el.style.position = 'relative';
  el.appendChild(overlay);
}

function hideLoading(containerId) {
  const el = document.getElementById(`loading-${containerId}`);
  if (el) el.remove();
}

/* ── Rank Badge Helper ─────────────────────────────────── */
function rankBadge(rank) {
  const cls = rank === 1 ? 'gold' : rank === 2 ? 'silver' : rank === 3 ? 'bronze' : 'other';
  const icon = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : rank;
  return `<span class="rank-badge ${cls}">${icon}</span>`;
}

/* ── Avatar Color ─────────────────────────────────────── */
const AVATAR_COLORS = [
  'linear-gradient(135deg,#6366F1,#8B5CF6)',
  'linear-gradient(135deg,#06B6D4,#3B82F6)',
  'linear-gradient(135deg,#10B981,#06B6D4)',
  'linear-gradient(135deg,#F59E0B,#EF4444)',
  'linear-gradient(135deg,#8B5CF6,#EC4899)',
];

function avatarColor(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

function avatarInitials(name) {
  return (name || '?').split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

/* ── Skill Tag ─────────────────────────────────────────── */
function skillTag(skillName, category = 'technical', extra = '') {
  return `<span class="skill-tag ${category}" ${extra}>${skillName}</span>`;
}

/* ── Proficiency Badge ──────────────────────────────────── */
function proficiencyBadge(level) {
  const colors = {
    expert:       'badge-secondary',
    advanced:     'badge-success',
    intermediate: 'badge-warning',
    beginner:     'badge-muted',
  };
  return `<span class="badge ${colors[level] || 'badge-muted'}">${level}</span>`;
}

/* ── Init on DOM load ───────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Animate in cards
  document.querySelectorAll('.stat-card, .card').forEach((el, i) => {
    el.style.animationDelay = `${i * 0.05}s`;
    el.classList.add('animate-in');
  });

  // Sidebar logout button
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', logout);
});
