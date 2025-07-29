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
        <h2 class="mb-4 text-center text-primary-neon">Manage Users</h2>
        <p class="text-center text-light-accent">View and manage registered users.</p>

        <h4 class="text-light-accent mb-3">Registered Users List</h4>
        <ul class="list-group custom-list-group">
          <li v-for="user in users" :key="user.id" class="list-group-item d-flex justify-content-between align-items-center custom-list-item">
            <span>
              <b class="text-primary-neon">{{ user.full_name }}</b> - <span class="text-light-accent">{{ user.email }}</span>
              <br>
              <small class="text-light-accent">Qualification: {{ user.qualification }} | DOB: {{ user.dob }}</small>
            </span>
            <div>
              <button class="btn btn-sm custom-icon-btn-danger" @click="deleteUser(user.id)">
                <i class="bi bi-trash-fill"></i>
              </button>
            </div>
          </li>
          <li v-if="users.length === 0" class="list-group-item custom-list-item text-center text-light-accent">No users found.</li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const users = ref([])

async function fetchUsers() {
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    // MODIFIED: Use the correct endpoint for Admin to fetch all users
    const response = await fetch('http://localhost:5000/api/admin/users', { // <--- CHANGED ENDPOINT
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { users.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load users: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching users:', error); alert('Network error. Could not connect to the server.'); }
}

onMounted(fetchUsers);

async function deleteUser(id) {
  if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) { return; }
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const response = await fetch(`http://localhost:5000/api/admin/users/${id}`, { // This endpoint is correct for DELETE
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      await fetchUsers(); // Re-fetch users
    } else {
      const errorData = await response.json();
      alert(`Failed to delete user: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) { console.error('Network error in deleteUser:', error); alert('Network error. Could not connect to the server.'); }
}

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
</style>
