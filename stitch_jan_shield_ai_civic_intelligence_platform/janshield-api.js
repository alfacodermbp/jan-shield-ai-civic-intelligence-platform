(function () {
  'use strict';

  var API_BASE_URL = window.JAN_SHIELD_API_URL ||
    ((location.hostname === 'localhost' || location.hostname === '127.0.0.1') ? location.protocol + '//' + location.hostname + ':3000' : location.origin);
  var routes = {
    dashboard: '/citizen_dashboard/code.html', analytics: '/authority_analytics_dashboard/code.html',
    'map view': '/systemic_issue_analysis/code.html', reports: '/report_a_grievance/code.html',
    'report an issue': '/report_a_grievance/code.html', 'report new grievance': '/report_a_grievance/code.html',
    'explore command center': '/authority_command_center_1/code.html', overview: '/authority_command_center_1/code.html',
    'authority panel': '/authority_command_center_1/code.html', 'citizen requests': '/authority_command_center_1/code.html',
    'systemic issues': '/systemic_issue_analysis/code.html', 'view all': '/authority_command_center_1/code.html'
  };
  var tokenKey = 'janShieldToken';
  var token = function () { return sessionStorage.getItem(tokenKey) || localStorage.getItem(tokenKey); };
  function notify(message, kind) {
    var node = document.createElement('div');
    node.textContent = message; node.setAttribute('role', 'status');
    node.style.cssText = 'position:fixed;right:20px;bottom:20px;z-index:9999;padding:12px 16px;border-radius:8px;background:' + (kind === 'error' ? '#ba1a1a' : '#131b2e') + ';color:#fff;font:14px Inter,sans-serif;box-shadow:0 4px 14px #0003';
    document.body.appendChild(node); setTimeout(function () { node.remove(); }, 3500);
  }
  async function request(path, options) {
    options = options || {}; var headers = Object.assign({}, options.headers || {});
    if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
    if (token()) headers.Authorization = 'Bearer ' + token();
    var response;
    try { response = await fetch(API_BASE_URL + path, Object.assign({}, options, { headers: headers })); }
    catch (error) { throw new Error('Unable to reach JAN-SHIELD API'); }
    var payload; try { payload = await response.json(); } catch (error) { throw new Error('Invalid API response'); }
    if (!response.ok || payload.success === false) throw new Error((payload.error && (payload.error.message || payload.error)) || 'Request failed');
    return payload.data;
  }
  function go(label) { if (routes[label]) location.href = routes[label]; }
  function wireNavigation() {
    document.querySelectorAll('a[href="#"]').forEach(function (link) {
      var label = link.textContent.trim().toLowerCase();
      if (routes[label]) link.href = routes[label]; else link.addEventListener('click', function (event) { event.preventDefault(); });
    });
    document.querySelectorAll('button').forEach(function (button) {
      var label = button.textContent.trim().toLowerCase();
      Object.keys(routes).some(function (key) { if (label.indexOf(key) !== -1) { button.addEventListener('click', function () { go(key); }); return true; } return false; });
      if (label.indexOf('print') !== -1 || label.indexOf('export') !== -1) button.addEventListener('click', function () { window.print(); });
      if (label.indexOf('share') !== -1) button.addEventListener('click', function () { navigator.clipboard && navigator.clipboard.writeText(location.href).then(function () { notify('Link copied'); }); });
      if (label.indexOf('notification') !== -1) button.addEventListener('click', function () { request('/api/notifications').then(function (items) { notify(items.length ? items.filter(function (n) { return !n.read; }).length + ' unread notifications' : 'No notifications'); }).catch(function (e) { notify(e.message, 'error'); }); });
      if (label.indexOf('emergency alert') !== -1) button.addEventListener('click', function () { notify('Emergency alert requires human authority confirmation.', 'error'); });
    });
  }
  function wireComplaintForm() {
    var fields = document.querySelectorAll('input.form-input, select.form-input, textarea.form-input');
    var button = Array.from(document.querySelectorAll('button')).find(function (item) { return /next: location/i.test(item.textContent); });
    if (!button || fields.length < 3) return;
    button.addEventListener('click', async function () {
      var title = fields[0].value.trim(), category = fields[1].value, description = fields[2].value.trim();
      if (title.length < 3 || description.length < 10 || !category) { notify('Enter a title, category, and description.', 'error'); return; }
      button.disabled = true;
      try {
        var result = await request('/api/complaints', { method: 'POST', body: JSON.stringify({ title: title, category: category, description: description }) });
        localStorage.setItem('janShieldComplaintId', result.id); button.textContent = 'Complaint ID: ' + result.id; button.dataset.complaintId = result.id; notify('Complaint submitted successfully.');
        button.disabled = false; button.addEventListener('click', function () { location.href = '/complaint_detail_resolution/code.html?id=' + encodeURIComponent(result.id); }, { once: true });
      } catch (error) { button.disabled = false; notify(error.message, 'error'); }
    });
  }
  function fillDashboard() {
    request('/api/analytics').then(function (data) {
      var values = document.querySelectorAll('.bento-item .font-headline-h3, .bento-item .font-headline-h4');
      if (values[0]) values[0].textContent = data.totalComplaints;
      if (values[1]) values[1].textContent = data.activeComplaints;
      if (values[2]) values[2].textContent = data.totalComplaints - data.activeComplaints;
    }).catch(function (e) { notify(e.message, 'error'); });
    request('/api/complaints?limit=5').then(function (result) { window.JanShieldComplaints = result.data || []; }).catch(function () {});
  }
  function fillAnalytics() {
    request('/api/analytics').then(function (data) {
      var cards = document.querySelectorAll('.font-headline-h1');
      if (cards[0]) cards[0].textContent = data.totalComplaints;
      if (cards[1]) cards[1].textContent = Math.round(data.resolutionRate || 0) + '%';
      if (cards[2]) cards[2].textContent = 'Demo';
    }).catch(function (e) { notify(e.message, 'error'); });
  }
  function fillComplaintDetail() {
    var id = new URLSearchParams(location.search).get('id') || localStorage.getItem('janShieldComplaintId'); if (!id) return;
    request('/api/complaints/' + encodeURIComponent(id)).then(function (complaint) {
      document.title = complaint.title + ' - JAN-SHIELD AI';
      var heading = document.querySelector('h1'); if (heading) heading.textContent = complaint.title;
      var text = document.querySelector('main p.font-body-md'); if (text) text.textContent = complaint.description;
      var badge = document.querySelector('.bg-secondary-fixed-dim'); if (badge) badge.lastChild.textContent = ' ' + complaint.status;
      var save = Array.from(document.querySelectorAll('button')).find(function (b) { return /save changes/i.test(b.textContent); });
      if (save) save.addEventListener('click', async function () {
        var selects = document.querySelectorAll('section select'); var statusMap = { 'Action Initiated': 'ACTION_INITIATED', 'Assigned to Crew': 'ASSIGNED', 'Under Resolution': 'IN_PROGRESS', Resolved: 'RESOLUTION_PENDING_VERIFICATION' };
        try { await request('/api/complaints/' + id, { method: 'PATCH', body: JSON.stringify({ status: statusMap[selects[1] && selects[1].value] || complaint.status }) }); notify('Complaint updated successfully.'); } catch (e) { notify(e.message, 'error'); }
      });
    }).catch(function (e) { notify(e.message, 'error'); });
  }
  function wireSearch() {
    document.querySelectorAll('input[placeholder*="Search"], input[placeholder*="search"]').forEach(function (input) {
      input.addEventListener('keydown', async function (event) { if (event.key !== 'Enter' || !input.value.trim()) return; try { var result = await request('/api/complaints?search=' + encodeURIComponent(input.value.trim())); notify((result.total || 0) + ' complaints found.'); } catch (e) { notify(e.message, 'error'); } });
    });
  }
  function wireEvidence() {
    var button = Array.from(document.querySelectorAll('button')).find(function (b) { return /upload documents/i.test(b.textContent); });
    if (!button) return;
    var input = document.createElement('input'); input.type = 'file'; input.accept = 'image/*,.pdf,.txt'; input.hidden = true; document.body.appendChild(input);
    button.addEventListener('click', function () { input.click(); });
    input.addEventListener('change', async function () {
      var id = new URLSearchParams(location.search).get('id') || localStorage.getItem('janShieldComplaintId'); if (!id || !input.files[0]) return;
      try { await request('/api/complaints/' + encodeURIComponent(id) + '/evidence', { method: 'POST', body: JSON.stringify({ filename: input.files[0].name, type: input.files[0].type.indexOf('image') === 0 ? 'image' : input.files[0].name.toLowerCase().endsWith('.pdf') ? 'pdf' : 'text' }) }); notify('Evidence metadata recorded.'); } catch (e) { notify(e.message, 'error'); }
    });
  }
  window.JanShieldAPI = { request: request, notify: notify, go: go, routes: routes };
  wireNavigation(); wireComplaintForm(); wireSearch(); wireEvidence();
  if (/citizen_dashboard/.test(location.pathname)) fillDashboard();
  if (/authority_analytics_dashboard/.test(location.pathname)) fillAnalytics();
  if (/complaint_detail_resolution/.test(location.pathname)) fillComplaintDetail();
  if (/authority_command_center_|systemic_issue_analysis/.test(location.pathname)) request('/api/analytics').catch(function () {});
}());
