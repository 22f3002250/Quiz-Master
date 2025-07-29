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
        <h2 class="mb-4 text-center text-primary-neon">Manage Chapters</h2>
        <div class="mb-3">
          <label class="form-label text-light-accent">Select Subject</label>
          <select v-model="selectedSubjectId" class="form-select custom-select">
            <option disabled value="">-- Select Subject --</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
        <form class="mb-4" @submit.prevent="addChapter" v-if="selectedSubjectId">
          <div class="mb-2">
            <label class="form-label text-light-accent">Chapter Name</label>
            <input v-model="chapterName" class="form-control custom-input" required />
          </div>
          <div class="mb-2">
            <label class="form-label text-light-accent">Description</label>
            <input v-model="chapterDesc" class="form-control custom-input" />
          </div>
          <button class="btn btn-success custom-btn-filled" type="submit">
            {{ editingId ? "Save Changes" : "Add Chapter" }}
          </button>
          <button v-if="editingId" class="btn btn-secondary ms-2 custom-btn-outline" @click="cancelEdit">Cancel</button>
        </form>
        <h4 v-if="selectedSubjectId" class="text-light-accent mb-3">Chapters List for {{ subjectName(selectedSubjectId) }}</h4>
        <ul class="list-group custom-list-group" v-if="selectedSubjectId">
          <li v-for="chapter in chapters" :key="chapter.id" class="list-group-item d-flex justify-content-between align-items-center custom-list-item">
            <span>
              <b class="text-primary-neon">{{ chapter.name }}</b> - <span class="text-light-accent">{{ chapter.description }}</span>
            </span>
            <div>
              <!-- MODIFIED: Edit Button to use icon -->
              <button class="btn btn-sm custom-btn-action me-2" @click="editChapter(chapter)">
                <i class="bi bi-pencil-fill"></i>
              </button>
              <!-- MODIFIED: Delete Button to use icon -->
              <button class="btn btn-sm custom-btn-action-danger" @click="deleteChapter(chapter.id)">
                <i class="bi bi-trash-fill"></i>
              </button>
            </div>
          </li>
          <li v-if="chapters.length === 0" class="list-group-item custom-list-item text-center text-light-accent">No chapters found for this subject.</li>
        </ul>
        <div v-else class="alert alert-info mt-3 custom-alert">Please select a subject to manage chapters.</div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const subjects = ref([])
const selectedSubjectId = ref('')
const chapterName = ref('')
const chapterDesc = ref('')
const chapters = ref([])
const editingId = ref(null)

function subjectName(id) {
  const subj = subjects.value.find(s => s.id === Number(id))
  return subj ? subj.name : ''
}

async function fetchSubjects() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Authentication token missing. Please log in.');
        router.push('/login');
        return;
    }
    const response = await fetch('http://localhost:5000/api/subjects', {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
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

async function fetchChapters(subjectId) {
  if (!subjectId) {
    chapters.value = [];
    return;
  }
  try {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Authentication token missing. Please log in.');
        router.push('/login');
        return;
    }
    const response = await fetch(`http://localhost:5000/api/subjects/${subjectId}/chapters`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) {
      chapters.value = await response.json();
    } else {
      const errorData = await response.json();
      console.error('Failed to load chapters:', errorData.message || response.statusText);
      alert(`Failed to load chapters: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) {
          router.push('/login');
      }
    }
  } catch (error) {
    console.error('Network error fetching chapters:', error);
    alert('Network error. Could not connect to the server.');
  }
}

onMounted(fetchSubjects);

watch(selectedSubjectId, (newSubjectId) => {
  fetchChapters(newSubjectId);
  cancelEdit();
});

async function addChapter() {
  if (!selectedSubjectId.value) {
    alert('Please select a subject first.');
    return;
  }

  const token = localStorage.getItem('token');
  if (!token) {
      alert('Authentication token missing. Please log in.');
      router.push('/login');
      return;
  }

  const chapterData = {
    name: chapterName.value,
    description: chapterDesc.value,
    subject_id: Number(selectedSubjectId.value)
  };

  let response;
  if (editingId.value) {
    response = await fetch(`http://localhost:5000/api/chapters/${editingId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(chapterData)
    });
  } else {
    response = await fetch(`http://localhost:5000/api/subjects/${selectedSubjectId.value}/chapters`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(chapterData)
    });
  }

  if (response.ok) {
    await fetchChapters(selectedSubjectId.value);
    chapterName.value = '';
    chapterDesc.value = '';
    editingId.value = null;
  } else {
    const errorData = await response.json();
    alert(`Failed to ${editingId.value ? 'update' : 'add'} chapter: ${errorData.message || response.statusText}`);
    if (response.status === 401 || response.status === 403) {
        router.push('/login');
    }
  }
}

function editChapter(chapter) {
  editingId.value = chapter.id;
  chapterName.value = chapter.name;
  chapterDesc.value = chapter.description;
  selectedSubjectId.value = chapter.subject_id;
}

async function deleteChapter(id) {
  if (!confirm('Are you sure you want to delete this chapter? This action cannot be undone.')) {
    return;
  }

  const token = localStorage.getItem('token');
  if (!token) {
      alert('Authentication token missing. Please log in.');
      router.push('/login');
      return;
  }

  try {
    const response = await fetch(`http://localhost:5000/api/chapters/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      await fetchChapters(selectedSubjectId.value);
      if (editingId.value === id) {
        cancelEdit();
      }
    } else {
      const errorData = await response.json();
      alert(`Failed to delete chapter: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) {
          router.push('/login');
      }
    }
  } catch (error) {
    console.error('Network error in deleteChapter:', error);
    alert('Network error. Could not connect to the server.');
  }
}

function cancelEdit() {
  editingId.value = null;
  chapterName.value = '';
  chapterDesc.value = '';
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
