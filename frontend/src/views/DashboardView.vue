<template>
  <div class="user-layout-container">
    <!-- Left Sidebar for Navigation -->
    <aside class="user-sidebar">
      <h3 class="sidebar-title text-primary-neon">User Menu</h3>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-button custom-btn-sidebar">Dashboard</router-link>
        <router-link to="/quizzes" class="nav-button custom-btn-sidebar">Attempt Quiz</router-link>
        <router-link to="/scores" class="nav-button custom-btn-sidebar">View Scores</router-link>
        <router-link to="/profile" class="nav-button custom-btn-sidebar">Profile</router-link>
      </nav>
      <button @click="logout" class="btn btn-danger w-100 custom-btn-logout">Logout</button>
    </aside>

    <!-- Main Content Area -->
    <main class="user-main-content">
      <div class="card p-4 shadow-lg rounded-3 content-card">
        <h2 class="mb-4 text-center text-primary-neon">Welcome to Quiz Practice!</h2>
        <p class="text-center text-light-accent">
          You are now logged in.<br>
          Use the menu on the left to navigate the platform.
        </p>
        <!-- Placeholder for user dashboard specific widgets/summary charts if any -->
        <div class="dashboard-widgets mt-4">
          <p class="text-center text-light-accent">Your personalized content and quiz recommendations will appear here.</p>
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

</style>
