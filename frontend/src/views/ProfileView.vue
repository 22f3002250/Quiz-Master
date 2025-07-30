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
        <h2 class="mb-4 text-center text-primary-neon">Your Profile</h2>

        <form @submit.prevent="updateProfile">
          <div class="mb-3">
            <label for="email" class="form-label text-light-accent">Email (Read-only)</label>
            <input v-model="email" type="email" class="form-control custom-input" id="email" readonly />
          </div>
          <div class="mb-3">
            <label for="full_name" class="form-label text-light-accent">Full Name</label>
            <input v-model="full_name" type="text" class="form-control custom-input" id="full_name" required />
          </div>
          <div class="mb-3">
            <label for="qualification" class="form-label text-light-accent">Qualification</label>
            <input v-model="qualification" type="text" class="form-control custom-input" id="qualification" required />
          </div>
          <div class="mb-3">
            <label for="dob" class="form-label text-light-accent">Date of Birth</label>
            <input v-model="dob" type="date" class="form-control custom-input" id="dob" required />
          </div>
          <button type="submit" class="btn custom-btn-filled" :disabled="loading">
            {{ loading ? "Saving..." : "Update Profile" }}
          </button>
          <div v-if="message" :class="['alert mt-3', messageType === 'success' ? 'alert-success' : 'alert-danger', 'custom-alert']">{{ message }}</div>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { jwtDecode } from 'jwt-decode';

const router = useRouter()
const email = ref('')
const full_name = ref('')
const qualification = ref('')
const dob = ref('')
const loading = ref(false)
const message = ref('')
const messageType = ref('')

async function fetchProfile() {
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const decodedToken = jwtDecode(token);
    // --- MODIFIED: Parse the 'sub' claim which contains the actual identity dictionary ---
    const identity = JSON.parse(decodedToken.sub); // Parse the JSON string from 'sub'
    const userId = identity.id; // Get user ID from the parsed identity object
    // --- END MODIFIED ---
    
    console.log("DEBUG: Fetching profile for userId:", userId);
    if (!userId) {
        console.error("ERROR: userId is undefined or null from token.");
        alert("Could not retrieve user ID from token. Please re-login.");
        router.push('/login');
        return;
    }

    const response = await fetch(`http://localhost:5000/api/users/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) {
      const userData = await response.json();
      email.value = userData.email;
      full_name.value = userData.full_name;
      qualification.value = userData.qualification;
      dob.value = userData.dob;
    } else {
      const errorData = await response.json();
      console.error('Failed to load profile:', errorData.message || response.statusText);
      alert(`Failed to load profile: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) {
    console.error('Network error fetching profile:', error);
    alert('Network error. Could not connect to the server.');
  }
}

async function updateProfile() {
  loading.value = true;
  message.value = '';
  messageType.value = '';

  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const decodedToken = jwtDecode(token);
    // --- MODIFIED: Parse the 'sub' claim for userId in updateProfile as well ---
    const identity = JSON.parse(decodedToken.sub);
    const userId = identity.id;
    // --- END MODIFIED ---

    const response = await fetch(`http://localhost:5000/api/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({
        full_name: full_name.value,
        qualification: qualification.value,
        dob: dob.value
      })
    });

    if (response.ok) {
      message.value = 'Profile updated successfully!';
      messageType.value = 'success';
    } else {
      const errorData = await response.json();
      message.value = errorData.message || 'Failed to update profile.';
      messageType.value = 'danger';
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) {
    console.error('Network error updating profile:', error);
    message.value = 'Network error. Could not connect to the server.';
    messageType.value = 'danger';
  } finally {
    loading.value = false;
  }
}

onMounted(fetchProfile);

function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* All common styles for user layout and content are in user.css */

/* Specific styles for forms and inputs */
.custom-input {
  background-color: #3d2766;
  border: 1px solid #6a4a9c;
  color: #e0e0e0;
  border-radius: 8px;
  padding: 10px 15px;
}
.custom-input:focus {
  background-color: #4a307a;
  border-color: #e060a8;
  box-shadow: 0 0 0 0.25rem rgba(224, 96, 168, 0.25);
  color: #e0e0e0;
}

.custom-btn-filled {
  background-color: #8a2be2;
  border-color: #8a2be2;
  border-radius: 10px;
  font-weight: bold;
  padding: 10px 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(138, 43, 226, 0.4);
}
.custom-btn-filled:hover {
  background-color: #7a1ee0;
  border-color: #7a1ee0;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(138, 43, 226, 0.6);
}

.custom-alert {
  background-color: #4a1a1a; /* Dark red for alerts */
  color: #ff8080; /* Light red text */
  border-color: #802020;
  border-radius: 8px;
}
.alert-success.custom-alert {
  background-color: #284a1a; /* Dark green for success */
  color: #80ff80; /* Light green text */
  border-color: #408020;
}
</style>