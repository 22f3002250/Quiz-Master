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
          <p class="text-light-accent">Here you can generate and view reports on user activity, quiz performance, and more.</p>
          <button class="btn custom-btn-filled mt-3">Generate Monthly Report</button>
          <button class="btn custom-btn-outline ms-2 mt-3">Export All Quizzes Data (CSV)</button>
        </div>

        <div class="mt-5">
          <h4 class="text-light-accent">Report Summary Placeholder</h4>
          <p class="text-muted">Detailed charts and tables will be displayed here.</p>
          <!-- Example placeholder for a chart or table -->
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
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.custom-btn-action {
  background-color: #5dbeff; /* Electric blue for small filled buttons */
  border-color: #5dbeff;
  color: #1a0f2d; /* Dark text for contrast */
  border-radius: 5px;
  font-weight: bold;
  padding: 5px 10px;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}
.custom-btn-action:hover {
  background-color: #2a9dff;
  border-color: #2a9dff;
  transform: translateY(-1px);
}

.custom-btn-action-danger {
  background-color: #e060a8; /* Neon pink for small danger buttons */
  border-color: #e060a8;
  color: #1a0f2d; /* Dark text for contrast */
  border-radius: 5px;
  font-weight: bold;
  padding: 5px 10px;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}
.custom-btn-action-danger:hover {
  background-color: #c04080;
  border-color: #c04080;
  transform: translateY(-1px);
}
.bg-dark-accent {
  background-color: #3d2766; /* Slightly lighter dark background for internal sections */
  border: 1px solid #4a2d73;
}
</style>
