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
        <h2 class="mb-4 text-center text-primary-neon">Manage Subjects</h2>
        <form class="mb-4" @submit.prevent="addSubject">
          <div class="mb-2">
            <label class="form-label text-light-accent">Subject Name</label>
            <input v-model="subjectName" class="form-control custom-input" required />
          </div>
          <div class="mb-2">
            <label class="form-label text-light-accent">Description</label>
            <input v-model="subjectDesc" class="form-control custom-input" />
          </div>
          <button class="btn custom-btn-filled" type="submit">
            {{ editingId ? "Save Changes" : "Add Subject" }}
          </button>
          <button v-if="editingId" class="btn custom-btn-outline ms-2" @click="cancelEdit">Cancel</button>
        </form>
        <h4 class="text-light-accent mb-3">Subjects List</h4>
        <ul class="list-group custom-list-group">
          <li v-for="subject in subjects" :key="subject.id" class="list-group-item d-flex justify-content-between align-items-center custom-list-item">
            <span>
              <b class="text-primary-neon">{{ subject.name }}</b> - <span class="text-light-accent">{{ subject.description }}</span>
            </span>
            <div>
              <button class="btn btn-sm custom-btn-action me-2" @click="editSubject(subject)">
                <i class="bi bi-pencil-fill"></i>
              </button>
              <button class="btn btn-sm custom-btn-action-danger" @click="deleteSubject(subject.id)">
                <i class="bi bi-trash-fill"></i>
              </button>
            </div>
          </li>
          <li v-if="subjects.length === 0" class="list-group-item custom-list-item text-center text-light-accent">No subjects found.</li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter();
const subjectName = ref('')
const subjectDesc = ref('')
const subjects = ref([])
const editingId = ref(null)

async function fetchSubjects() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Authentication token missing. Please log in.');
        router.push('/login');
        return;
    }

    const response = await fetch('http://localhost:5000/api/subjects', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      subjects.value = await response.json();
    } else {
      const errorData = await response.json();
      console.error('Failed to load subjects:', errorData.message || response.statusText);
      alert(`Failed to load subjects: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) {
          router.push('/login');
      }
    }
  } catch (error) {
    console.error('Network error fetching subjects:', error);
    alert('Network error. Could not connect to the server.');
  }
}

onMounted(fetchSubjects);

async function addSubject() {
  const token = localStorage.getItem('token');
  if (!token) {
      alert('Authentication token missing. Please log in.');
      router.push('/login');
      return;
  }

  const url = editingId.value
    ? `http://localhost:5000/api/subjects/${editingId.value}`
    : 'http://localhost:5000/api/subjects';

  const method = editingId.value ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ name: subjectName.value, description: subjectDesc.value })
    });

    if (response.ok) {
      await fetchSubjects();
      subjectName.value = '';
      subjectDesc.value = '';
      editingId.value = null;
    } else {
      const errorData = await response.json();
      alert(`Failed to ${editingId.value ? "update" : "add"} subject: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) {
          router.push('/login');
      }
    }
  } catch (error) {
    console.error('Network error in addSubject:', error);
    alert('Network error. Could not connect to the server.');
  }
}

function editSubject(subject) {
  editingId.value = subject.id;
  subjectName.value = subject.name;
  subjectDesc.value = subject.description;
}

async function deleteSubject(id) {
  if (!confirm('Are you sure you want to delete this subject? This action cannot be undone.')) {
    return;
  }

  const token = localStorage.getItem('token');
  if (!token) {
      alert('Authentication token missing. Please log in.');
      router.push('/login');
      return;
  }

  try {
    const response = await fetch(`http://localhost:5000/api/subjects/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      await fetchSubjects();
      if (editingId.value === id) {
        cancelEdit();
      }
    } else {
      const errorData = await response.json();
      alert(`Failed to delete subject: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) {
          router.push('/login');
      }
    }
  } catch (error) {
    console.error('Network error in deleteSubject:', error);
    alert('Network error. Could not connect to the server.');
  }
}

function cancelEdit() {
  editingId.value = null;
  subjectName.value = '';
  subjectDesc.value = '';
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
