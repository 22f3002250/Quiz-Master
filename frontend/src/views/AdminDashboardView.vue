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
        <h2 class="mb-4 text-center text-primary-neon">Admin Dashboard</h2>
        <p class="text-center text-light-accent">
          Welcome, Quiz Master!<br>
          Use the menu on the left to manage the platform.
        </p>

        <!-- Summary Statistics -->
        <div class="row mt-4 text-center">
          <div class="col-md-4 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Total Users</h5>
              <p class="fs-4 text-light-accent">{{ stats.total_users }}</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Total Subjects</h5>
              <p class="fs-4 text-light-accent">{{ stats.total_subjects }}</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Total Quizzes</h5>
              <p class="fs-4 text-light-accent">{{ stats.total_quizzes }}</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Total Questions</h5>
              <p class="fs-4 text-light-accent">{{ stats.total_questions }}</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Total Scores Recorded</h5>
              <p class="fs-4 text-light-accent">{{ stats.total_scores }}</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Average Quiz Score</h5>
              <p class="fs-4 text-light-accent">{{ stats.average_score }}%</p>
            </div>
          </div>
        </div>

        <!-- Charts Section -->
        <div class="row mt-5">
          <h4 class="text-primary-neon text-center mb-4">Analytics Overview</h4>
          <div class="col-md-6 mb-4">
            <div class="chart-card p-3 rounded custom-list-item">
              <h5 class="text-light-accent text-center mb-3">Content Distribution</h5>
              <!-- Ensure min-height for charts to render properly -->
              <div style="height: 250px;">
                <Bar :data="contentChartData" :options="chartOptions" />
              </div>
            </div>
          </div>
          <div class="col-md-6 mb-4">
            <div class="chart-card p-3 rounded custom-list-item">
              <h5 class="text-light-accent text-center mb-3">User Engagement</h5>
              <div style="height: 250px;">
                <Doughnut :data="userEngagementChartData" :options="chartOptions" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
// Import Chart.js components
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement } from 'chart.js'

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const router = useRouter()
const stats = ref({
  total_users: 0,
  total_subjects: 0,
  total_chapters: 0,
  total_quizzes: 0,
  total_questions: 0,
  total_scores: 0,
  average_score: 0
})

// Chart Data (Reactive)
const contentChartData = computed(() => ({
  labels: ['Subjects', 'Chapters', 'Quizzes', 'Questions'],
  datasets: [
    {
      label: 'Count',
      // MODIFIED: Use more vibrant and distinct neon colors
      backgroundColor: ['#e060a8', '#5dbeff', '#8a2be2', '#28a745'],
      borderColor: 'rgba(255, 255, 255, 0.1)', // Subtle border for bars/segments
      borderWidth: 1,
      data: [stats.value.total_subjects, stats.value.total_chapters, stats.value.total_quizzes, stats.value.total_questions]
    }
  ]
}))

const userEngagementChartData = computed(() => ({
  labels: ['Total Users', 'Quizzes Taken', 'Avg Score'],
  datasets: [
    {
      label: 'Metrics',
      // MODIFIED: Use more vibrant and distinct neon colors
      backgroundColor: ['#e060a8', '#5dbeff', '#8a2be2'],
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      data: [stats.value.total_users, stats.value.total_scores, stats.value.average_score]
    }
  ]
}))

// Chart Options (Common) - Heavily refined for dark theme and readability
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: { // NEW: Add chart title for clarity
      display: true,
      text: 'Overview', // Placeholder, can be overridden per chart
      color: '#e0e0e0' // White title color
    },
    legend: {
      labels: {
        color: '#e0e0e0', // White legend text
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(43, 26, 71, 0.9)', // Dark card background for tooltip
      borderColor: '#e060a8', // Neon pink border
      borderWidth: 1,
      titleColor: '#e0e0e0', // White title in tooltip
      bodyColor: '#e0e0e0', // White body in tooltip
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += context.parsed.y;
          } else if (context.parsed.x !== null) { // For Doughnut chart
            label += context.parsed.x;
          }
          return label;
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#c0b0d0' // Light accent color for x-axis labels
      },
      grid: {
        color: 'rgba(74, 45, 115, 0.3)' // Subtle grid lines
      },
      title: { // NEW: Axis title
        display: true,
        text: 'Category',
        color: '#e0e0e0'
      }
    },
    y: {
      ticks: {
        color: '#c0b0d0', // Light accent color for y-axis labels
        beginAtZero: true // Ensure y-axis starts at zero
      },
      grid: {
        color: 'rgba(74, 45, 115, 0.3)'
      },
      title: { // NEW: Axis title
        display: true,
        text: 'Count / Value',
        color: '#e0e0e0'
      }
    }
  }
}


// --- Fetching Functions ---
async function fetchAdminStats() {
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    const response = await fetch('http://localhost:5000/api/admin/dashboard/stats', {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { stats.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load admin stats: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching admin stats:', error); alert('Network error. Could not connect to the server.'); }
}

// --- Lifecycle Hooks ---
onMounted(fetchAdminStats);

// --- Logout Function ---
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* No component-specific styles needed here if all are common and in admin.css */

.stat-card, .chart-card {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); /* Slightly stronger shadow for cards */
  transition: transform 0.2s ease;
}
.stat-card:hover, .chart-card:hover {
  transform: translateY(-3px);
}
</style>
