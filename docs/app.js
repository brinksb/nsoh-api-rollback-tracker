// Detect repo info from GitHub Pages URL
function getRepoInfo() {
    const hostname = window.location.hostname;

    // GitHub Pages: {username}.github.io/{repo}
    if (hostname.endsWith('.github.io') && !hostname.endsWith('.pages.github.io')) {
        const username = hostname.replace('.github.io', '');
        const repo = window.location.pathname.split('/')[1] || 'nsoh-api-rollback-tracker';
        return { username, repo };
    }

    // Private GitHub Pages (enterprise): check body data attribute
    const repoConfig = document.body.dataset.repo;
    if (repoConfig) {
        const [username, repo] = repoConfig.split('/');
        return { username, repo };
    }

    return null;
}

function getDataBaseUrl() {
    const hostname = window.location.hostname;

    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return '../data';
    }

    const repoInfo = getRepoInfo();
    if (repoInfo) {
        return `https://raw.githubusercontent.com/${repoInfo.username}/${repoInfo.repo}/main/data`;
    }

    // Default fallback
    return '../data';
}

function updateGitHubLink() {
    const link = document.getElementById('github-link');
    if (!link) return;

    const repoInfo = getRepoInfo();
    if (repoInfo) {
        link.href = `https://github.com/${repoInfo.username}/${repoInfo.repo}`;
    } else {
        link.style.display = 'none';
    }
}

const BASE_URL = getDataBaseUrl();

async function fetchJSON(path) {
    try {
        const response = await fetch(`${BASE_URL}/${path}`);
        if (!response.ok) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch ${path}:`, error);
        return null;
    }
}

function formatTimestamp(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
    });
}

function formatRelativeTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
}

async function loadLatestComparison() {
    const container = document.getElementById('latest-result');
    const data = await fetchJSON('rollbacks/latest_comparison.json');

    if (!data) {
        container.innerHTML = '<p class="no-data">No comparison data available yet. Run the tracker to generate data.</p>';
        return null;
    }

    const hasRollback = data.rollbacks_detected > 0;
    const statusClass = hasRollback ? 'status-rollback' : 'status-ok';
    const statusText = hasRollback
        ? `Rollback detected: ${data.rollbacks_detected}/${data.total_locations} locations (${data.rollback_percentage}%)`
        : `All clear: ${data.total_locations} locations checked`;

    container.innerHTML = `
        <div class="latest-status">
            <div class="status-indicator ${statusClass}"></div>
            <div class="latest-details">
                <strong>${statusText}</strong>
                <span>${formatTimestamp(data.timestamp)}</span>
            </div>
        </div>
    `;

    return data;
}

async function loadRollbackLog() {
    const container = document.getElementById('rollback-list');
    const data = await fetchJSON('rollbacks/rollback_log.json');

    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No rollbacks detected yet.</p>';
        return [];
    }

    // Sort by timestamp descending (most recent first)
    const sorted = [...data].sort((a, b) =>
        new Date(b.timestamp) - new Date(a.timestamp)
    );

    container.innerHTML = sorted.map(event => {
        const badgeClass = event.is_dataset_level ? 'badge-dataset' : 'badge-row';
        const badgeText = event.is_dataset_level ? 'Dataset' : 'Row';

        return `
            <div class="rollback-event">
                <div class="rollback-header">
                    <span class="rollback-time">${formatTimestamp(event.timestamp)}</span>
                    <span class="rollback-badge ${badgeClass}">${badgeText}</span>
                </div>
                <div class="rollback-stats">
                    ${event.rollbacks_detected}/${event.total_locations} locations affected (${event.rollback_percentage}%)
                </div>
            </div>
        `;
    }).join('');

    return sorted;
}

function updateSummary(rollbacks, latest) {
    const totalEl = document.getElementById('total-rollbacks');
    const datasetEl = document.getElementById('dataset-level');
    const rowEl = document.getElementById('row-level');
    const lastCheckEl = document.getElementById('last-check');

    if (rollbacks && rollbacks.length > 0) {
        totalEl.textContent = rollbacks.length;
        datasetEl.textContent = rollbacks.filter(r => r.is_dataset_level).length;
        rowEl.textContent = rollbacks.filter(r => !r.is_dataset_level).length;
    } else {
        totalEl.textContent = '0';
        datasetEl.textContent = '0';
        rowEl.textContent = '0';
    }

    if (latest) {
        lastCheckEl.textContent = formatRelativeTime(latest.timestamp);
    } else {
        lastCheckEl.textContent = 'Never';
    }
}

async function init() {
    updateGitHubLink();

    const [latest, rollbacks] = await Promise.all([
        loadLatestComparison(),
        loadRollbackLog()
    ]);

    updateSummary(rollbacks, latest);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
