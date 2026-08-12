(function () {
  const API_BASE_URL = window.JAN_SHIELD_API_URL || (location.hostname === 'localhost' || location.hostname === '127.0.0.1'
    ? 'http://' + location.hostname + ':3000'
    : location.origin);
  async function request(path, options) {
    const response = await fetch(API_BASE_URL + path, Object.assign({ headers: { 'Content-Type': 'application/json' } }, options || {}));
    const payload = await response.json();
    if (!response.ok || payload.success === false) throw new Error(payload.error && payload.error.message || 'Request failed');
    return payload.data;
  }
  window.JanShieldAPI = { request };
  const path = location.pathname;
  const pages = {
    dashboard: '/citizen_dashboard/code.html',
    analytics: '/authority_analytics_dashboard/code.html',
    'map view': '/systemic_issue_analysis/code.html',
    reports: '/report_a_grievance/code.html',
    'report an issue': '/report_a_grievance/code.html',
    'report new grievance': '/report_a_grievance/code.html',
    'explore command center': '/authority_command_center_1/code.html'
  };
  document.querySelectorAll('a[href="#"]').forEach(function (link) {
    const label = link.textContent.trim().toLowerCase();
    if (pages[label]) link.href = pages[label];
    else link.addEventListener('click', function (event) { event.preventDefault(); });
  });
  document.querySelectorAll('button').forEach(function (button) {
    const label = button.textContent.trim().toLowerCase();
    Object.keys(pages).some(function (key) {
      if (label.indexOf(key) !== -1) { button.addEventListener('click', function () { location.href = pages[key]; }); return true; }
      return false;
    });
  });
  if (path.indexOf('/report_a_grievance/') !== -1) {
    const fields = document.querySelectorAll('input.form-input, select.form-input, textarea.form-input');
    const button = Array.from(document.querySelectorAll('button')).find(function (item) { return item.textContent.indexOf('Next: Location') !== -1; });
    if (button && fields.length >= 3) button.addEventListener('click', async function () {
      button.disabled = true;
      try {
        const result = await request('/api/complaints', { method: 'POST', body: JSON.stringify({ title: fields[0].value, category: fields[1].value, description: fields[2].value }) });
        localStorage.setItem('janShieldComplaintId', result.id);
        button.textContent = 'Complaint ID: ' + result.id;
        button.dataset.complaintId = result.id;
        button.disabled = false;
      } catch (error) { button.disabled = false; button.textContent = error.message; }
    });
  }
  if (path.indexOf('/citizen_dashboard/') !== -1) {
    request('/api/analytics').then(function (data) {
      const values = document.querySelectorAll('.bento-item .font-headline-h3, .bento-item .font-headline-h4');
      if (values[0]) values[0].textContent = data.totalComplaints;
      if (values[1]) values[1].textContent = data.activeComplaints;
      if (values[2]) values[2].textContent = data.totalComplaints - data.activeComplaints;
    }).catch(function () {});
  }
  if (path.indexOf('/complaint_detail_resolution/') !== -1) {
    const id = new URLSearchParams(location.search).get('id') || localStorage.getItem('janShieldComplaintId');
    if (id) request('/api/complaints/' + encodeURIComponent(id)).then(function (complaint) {
      document.title = complaint.title + ' - JAN-SHIELD AI';
      const heading = document.querySelector('h1, h2');
      if (heading) heading.textContent = complaint.title;
    }).catch(function () {});
  }
  if (path.indexOf('/authority_analytics_dashboard/') !== -1 || path.indexOf('/authority_command_center_') !== -1) {
    request('/api/analytics').catch(function () {});
  }
}());
