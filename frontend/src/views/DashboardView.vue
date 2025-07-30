<template>
  <div class="user-layout-container">
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

    <main class="user-main-content">
      <div class="card p-4 shadow-lg rounded-3 content-card">
        <h2 class="mb-4 text-center text-primary-neon">Welcome to Quiz Master!</h2>
        <p class="text-center text-light-accent">
          You are now logged in.<br>
          Use the menu on the left to navigate the platform.
        </p>

        <div class="row mt-4 text-center">
          <div class="col-md-6 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Quizzes Attempted</h5>
              <p class="fs-4 text-light-accent">{{ userStats.total_quizzes_attempted }}</p>
            </div>
          </div>
          <div class="col-md-6 mb-3">
            <div class="stat-card p-3 rounded custom-list-item">
              <h5 class="text-primary-neon">Your Average Score</h5>
              <p class="fs-4 text-light-accent">{{ userStats.average_user_score }}%</p>
            </div>
          </div>
        </div>

        <div class="row mt-5">
          <h4 class="text-primary-neon text-center mb-4">Your Performance Overview</h4>
          <div class="col-md-12 mb-4">
            <div class="chart-card p-3 rounded custom-list-item">
              <h5 class="text-light-accent text-center mb-3">Quiz Performance Summary</h5>
              <div style="height: 250px;">
                <Bar :data="userPerformanceChartData" :options="chartOptions" />
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
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const router = useRouter()
const userStats = ref({
  total_quizzes_attempted: 0,
  average_user_score: 0
})

const userPerformanceChartData = computed(() => ({
  labels: ['Quizzes Attempted', 'Average Score'],
  datasets: [
    {
      label: 'Value',
      backgroundColor: ['#e060a8', '#5dbeff'],
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      data: [userStats.value.total_quizzes_attempted, userStats.value.average_user_score]
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Your Quiz Stats',
      color: '#e0e0e0'
    },
    legend: {
      labels: {
        color: '#e0e0e0',
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(43, 26, 71, 0.9)',
      borderColor: '#e060a8',
      borderWidth: 1,
      titleColor: '#e0e0e0',
      bodyColor: '#e0e0e0',
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += context.parsed.y;
          }
          return label;
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#c0b0d0'
      },
      grid: {
        color: 'rgba(74, 45, 115, 0.3)'
      },
      title: {
        display: true,
        text: 'Metric',
        color: '#e0e0e0'
      }
    },
    y: {
      ticks: {
        color: '#c0b0d0',
        beginAtZero: true
      },
      grid: {
        color: 'rgba(74, 45, 115, 0.3)'
      },
      title: {
        display: true,
        text: 'Value',
        color: '#e0e0e0'
      }
    }
  }
}

// MODIFIED: fetchUserStats now accepts a 'bypassCache' argument
async function fetchUserStats(bypassCache = false) {
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    
    const url = new URL('http://localhost:5000/api/user/dashboard/stats');
    if (bypassCache) {
      url.searchParams.append('cache_bust', Date.now());
    }

    const response = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { userStats.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load user stats: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching user stats:', error); alert('Network error. Could not connect to the server.'); }
}

onMounted(() => fetchUserStats());

function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* All common styles for user layout and content are in user.css */

.stat-card, .chart-card {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease;
}
.stat-card:hover, .chart-card:hover {
  transform: translateY(-3px);
}
</style>
