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
        <h2 class="mb-4 text-center text-primary-neon">Your Quiz Scores</h2>

        <h4 class="text-light-accent mb-3">Past Attempts</h4>
        <ul class="list-group custom-list-group">
          <li v-for="score in scores" :key="score.id" class="list-group-item d-flex justify-content-between align-items-center custom-list-item">
            <span>
              <b class="text-primary-neon">Quiz: {{ getQuizTitle(score.quiz_id) }}</b>
              <br>
              <small class="text-light-accent">Score: {{ score.score }} | Attempted On: {{ formatDate(score.attempt_timestamp) }}</small>
            </span>
            <!-- You could add a "View Details" button here later -->
          </li>
          <li v-if="scores.length === 0" class="list-group-item custom-list-item text-center text-light-accent">No quiz scores recorded yet.</li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const scores = ref([])
const quizzes = ref([]) // To store quizzes for displaying titles

// Helper to format date
const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Helper to get quiz title by ID
const getQuizTitle = (quizId) => {
  const quiz = quizzes.value.find(q => q.id === quizId);
  return quiz ? quiz.title : 'Unknown Quiz';
}

// --- Fetching Functions ---
async function fetchScores() {
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    const response = await fetch('http://localhost:5000/api/scores', { // NEW API ENDPOINT
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { scores.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load scores: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching scores:', error); alert('Network error. Could not connect to the server.'); }
}

async function fetchAllQuizzes() {
  // This is a simplified fetch; ideally, you'd fetch only quizzes relevant to the user's scores
  // or have an endpoint that returns scores with quiz details.
  try {
    const token = localStorage.getItem('token');
    if (!token) { return; } // Don't alert/redirect here, already handled by fetchScores
    const response = await fetch('http://localhost:5000/api/quizzes/all', { // You'll need a new API endpoint for all quizzes (admin-only, or a user-accessible list)
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { quizzes.value = await response.json(); }
    else { console.error('Failed to load all quizzes for score display:', response.statusText); }
  } catch (error) { console.error('Network error fetching all quizzes:', error); }
}

// --- Lifecycle Hooks ---
onMounted(async () => {
  await fetchScores();
  await fetchAllQuizzes(); // Fetch all quizzes to resolve quiz titles
});

// --- Logout Function ---
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* All common styles for user layout and content are in user.css */
/* No specific styles needed here if all are common */
</style>
