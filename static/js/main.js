/**
 * main.js — Vault global JavaScript
 * - Mobile sidebar toggle
 * - Global search with debounce
 * - Password visibility toggle
 * - Auto-dismiss alerts
 */

document.addEventListener('DOMContentLoaded', () => {

  // ─── Mobile Sidebar ───────────────────────────────────────────────────────
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar   = document.getElementById('sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          e.target !== toggleBtn) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ─── Global Search (debounced) ────────────────────────────────────────────
  const searchInput   = document.getElementById('globalSearch');
  const searchResults = document.getElementById('searchResults');

  if (searchInput && searchResults) {
    let debounceTimer;

    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const q = searchInput.value.trim();

      if (!q) {
        searchResults.classList.add('d-none');
        searchResults.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res  = await fetch(`/search?q=${encodeURIComponent(q)}`);
          const data = await res.json();
          renderSearchResults(data, q);
        } catch (err) {
          console.error('Search error:', err);
        }
      }, 250);
    });

    // Close on Escape
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        searchResults.classList.add('d-none');
        searchInput.value = '';
      }
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.classList.add('d-none');
      }
    });
  }

  function renderSearchResults(data, q) {
    const total = data.files.length + data.notes.length + data.links.length + data.passwords.length;

    if (total === 0) {
      searchResults.innerHTML = `<div class="search-item text-muted">No results for "<strong>${escHtml(q)}</strong>"</div>`;
      searchResults.classList.remove('d-none');
      return;
    }

    let html = '';

    if (data.files.length) {
      html += `<div class="search-section">Files</div>`;
      data.files.forEach(f => {
        html += `<a class="search-item d-block text-decoration-none" href="/files/">
          <span class="si-name">${escHtml(f.name)}</span>
          <span class="si-meta">${escHtml(f.size)}</span>
        </a>`;
      });
    }

    if (data.notes.length) {
      html += `<div class="search-section">Notes</div>`;
      data.notes.forEach(n => {
        html += `<a class="search-item d-block text-decoration-none" href="/notes/${n.id}">
          <span class="si-name">${escHtml(n.title)}</span>
          <span class="si-meta">${escHtml(n.tags)}</span>
        </a>`;
      });
    }

    if (data.links.length) {
      html += `<div class="search-section">Links</div>`;
      data.links.forEach(l => {
        html += `<a class="search-item d-block text-decoration-none" href="/links/" >
          <span class="si-name">${escHtml(l.title)}</span>
          <span class="si-meta">${escHtml(l.url)}</span>
        </a>`;
      });
    }

    if (data.passwords.length) {
      html += `<div class="search-section">Passwords</div>`;
      data.passwords.forEach(p => {
        html += `<a class="search-item d-block text-decoration-none" href="/passwords/">
          <span class="si-name">${escHtml(p.site)}</span>
          <span class="si-meta">${escHtml(p.user)}</span>
        </a>`;
      });
    }

    searchResults.innerHTML = html;
    searchResults.classList.remove('d-none');
  }

  // ─── Auto-dismiss Alerts ──────────────────────────────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert?.close();
    }, 5000);
  });

  // ─── CSRF token in AJAX headers ───────────────────────────────────────────
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

  if (csrfToken) {
    // Attach to all fetch calls automatically if using a wrapper
    window._csrfToken = csrfToken;
  }

});

// ─── Utility: Toggle Password Visibility ──────────────────────────────────────
function togglePass(inputId) {
  const input = document.getElementById(inputId);
  const eyeId = inputId + '-eye';
  const eye   = document.getElementById(eyeId);

  if (!input) return;

  if (input.type === 'password') {
    input.type = 'text';
    if (eye) eye.className = 'bi bi-eye-slash';
  } else {
    input.type = 'password';
    if (eye) eye.className = 'bi bi-eye';
  }
}

// ─── Utility: HTML Escape ─────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
