<template>
  <div class="admin-layout-container">
    <!-- Left Sidebar for Navigation -->
    <aside class="admin-sidebar">
      <h3 class="sidebar-title text-primary-neon">Admin Menu</h3>
      <nav class="sidebar-nav">
        <router-link to="/admin/subjects" class="nav-button custom-btn-sidebar">Create & Manage Subjects</router-link>
        <router-link to="/admin/chapters" class="nav-button custom-btn-sidebar">Add & Manage Chapters</router-link>
        <router-link to="/admin/quizzes" class="nav-button custom-btn-sidebar">Create & Manage Quizzes</router-link>
        <router-link to="/admin/users" class="nav-button custom-btn-sidebar">View & Manage Users</router-link>
        <router-link to="/admin/reports" class="nav-button custom-btn-sidebar">View Reports & Analytics</router-link>
      </nav>
      <button @click="logout" class="btn btn-danger w-100 custom-btn-logout">Logout</button>
    </aside>

    <!-- Main Content Area -->
    <main class="admin-main-content">
      <div class="card p-4 shadow-lg rounded-3 content-card">
        <h2 class="mb-4 text-center text-primary-neon">Reports & Analytics</h2>
        <p class="text-center text-light-accent">This section will provide various reports and analytics.</p>

        <div class="mt-4 text-center">
          <p class="text-light-accent">Generate and view reports on user activity, quiz performance, and more.</p>
          <button class="btn custom-btn-filled mt-3" @click="generateMonthlyReport">Generate Monthly Report</button>
          <button class="btn custom-btn-outline ms-2 mt-3" @click="exportUsersToCsv">Export All Users Data (CSV)</button>
        </div>

        <div class="mt-5">
          <h4 class="text-light-accent">Report Summary Placeholder</h4>
          <p class="text-muted">Detailed charts and tables will be displayed here.</p>
          <div class="p-3 bg-dark-accent rounded" style="min-height: 200px;">
            <p class="text-center text-light-accent">Chart/Table visualization area</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

async function exportUsersToCsv() {
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const response = await fetch('http://localhost:5000/api/admin/reports/export-csv', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'users_report.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      alert('CSV export completed successfully! Your download should start shortly.');
    } else {
      const errorText = await response.text();
      try {
        const errorData = JSON.parse(errorText);
        alert(`Failed to initiate CSV export: ${errorData.message || response.statusText}`);
      } catch {
        alert(`Failed to initiate CSV export: ${errorText || response.statusText}`);
      }
      
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) {
    console.error('Network error initiating CSV export:', error);
    alert('Network error. Could not connect to the server.');
  }
}

async function generateMonthlyReport() {
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const response = await fetch('http://localhost:5000/api/admin/reports/generate-monthly', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      // --- MODIFIED: Handle HTML download on the frontend ---
      const blob = await response.blob(); // Get the response as a Blob
      const url = window.URL.createObjectURL(blob); // Create a temporary URL
      const a = document.createElement('a'); // Create a temporary anchor element
      a.href = url;
      // Generate a dynamic filename for the HTML report
      a.download = `monthly_report_${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}.html`; 
      document.body.appendChild(a); // Append to body to make it clickable
      a.click(); // Programmatically click to trigger download
      a.remove(); // Clean up the element
      window.URL.revokeObjectURL(url); // Revoke the URL

      alert('Monthly report generated successfully! Your download should start shortly.');
      // --- END MODIFIED ---
    } else {
      const errorText = await response.text();
      try {
        const errorData = JSON.parse(errorText);
        alert(`Failed to initiate monthly report: ${errorData.message || response.statusText}`);
      } catch {
        alert(`Failed to initiate monthly report: ${errorText || response.statusText}`);
      }
      
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) {
    console.error('Network error initiating monthly report:', error);
    alert('Network error. Could not connect to the server.');
  }
}

function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* Only specific styles for this component, common styles are in admin.css */

.bg-dark-accent {
  background-color: #3d2766; /* Slightly lighter dark background for internal sections */
  border: 1px solid #4a2d73;
}
</style>
