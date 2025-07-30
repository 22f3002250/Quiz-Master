<template>
  <div class="admin-layout-container">
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

    <main class="admin-main-content">
      <div class="card p-4 shadow-lg rounded-3 content-card">
        <h2 class="mb-4 text-center text-primary-neon">Manage Quizzes</h2>

        <!-- Select Subject and Chapter -->
        <div class="mb-3">
          <label class="form-label text-light-accent">Select Subject</label>
          <select v-model="selectedSubjectId" class="form-select custom-select">
            <option disabled value="">-- Select Subject --</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
        <div class="mb-3" v-if="selectedSubjectId">
          <label class="form-label text-light-accent">Select Chapter</label>
          <select v-model="selectedChapterId" class="form-select custom-select">
            <option disabled value="">-- Select Chapter --</option>
            <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
              {{ chapter.name }}
            </option>
          </select>
        </div>

        <!-- Quiz Form -->
        <form class="mb-4" @submit.prevent="addQuiz" v-if="selectedChapterId">
          <h4 class="text-light-accent mb-3">Quiz Details</h4>
          <div class="mb-2">
            <label class="form-label text-light-accent">Quiz Title</label>
            <input v-model="quizTitle" class="form-control custom-input" required />
          </div>
          <div class="mb-2">
            <label class="form-label text-light-accent">Description</label>
            <input v-model="quizDescription" class="form-control custom-input" />
          </div>
          <div class="mb-2">
            <label class="form-label text-light-accent">Duration (minutes)</label>
            <input v-model.number="quizDuration" type="number" class="form-control custom-input" required min="1" />
          </div>
          <div class="mb-2">
            <label class="form-label text-light-accent">Date of Quiz</label>
            <input v-model="quizDate" type="date" class="form-control custom-input" required />
          </div>
          <button class="btn custom-btn-filled" type="submit">
            {{ editingQuizId ? "Save Quiz Changes" : "Add Quiz" }}
          </button>
          <button v-if="editingQuizId" class="btn custom-btn-outline ms-2" @click="cancelEditQuiz">Cancel</button>
        </form>

        <!-- Search Input Field for Quizzes -->
        <div class="mb-3" v-if="selectedChapterId">
          <label class="form-label text-light-accent">Search Quizzes</label>
          <input v-model="searchQuizQuery" @input="fetchQuizzesWithSearch" class="form-control custom-input" placeholder="Search by title or description" />
        </div>

        <!-- Quizzes List -->
        <h4 v-if="selectedChapterId" class="text-light-accent mb-3">Quizzes for {{ chapterName(selectedChapterId) }}</h4>
        <ul class="list-group custom-list-group" v-if="selectedChapterId">
          <li v-for="quiz in quizzes" :key="quiz.id" class="list-group-item d-flex justify-content-between align-items-center custom-list-item">
            <span>
              <b class="text-primary-neon">{{ quiz.title }}</b> - <span class="text-light-accent">{{ quiz.description }}</span>
              <br>
              <small class="text-light-accent">Duration: {{ quiz.time_duration }} mins | Date: {{ quiz.date_of_quiz }}</small>
            </span>
            <div>
              <button class="btn btn-sm custom-icon-btn me-2" @click="editQuiz(quiz)">
                <i class="bi bi-pencil-fill"></i>
              </button>
              <button class="btn btn-sm custom-icon-btn-danger me-2" @click="deleteQuiz(quiz.id)">
                <i class="bi bi-trash-fill"></i>
              </button>
              <button class="btn btn-sm custom-btn-outline" @click="selectQuizForQuestions(quiz)">
                Manage Questions
              </button>
            </div>
          </li>
          <li v-if="quizzes.length === 0" class="list-group-item custom-list-item text-center text-light-accent">No quizzes found for this chapter.</li>
        </ul>

        <!-- Question Form (Visible only if a quiz is selected for question management) -->
        <div v-if="selectedQuizForQuestionsId" class="mt-5">
          <h3 class="text-primary-neon text-center mb-4">Manage Questions for "{{ quizTitleById(selectedQuizForQuestionsId) }}"</h3>
          <form class="mb-4" @submit.prevent="addQuestion">
            <div class="mb-2">
              <label class="form-label text-light-accent">Question Text</label>
              <textarea v-model="questionText" class="form-control custom-input" rows="3" required></textarea>
            </div>
            <div class="mb-2">
              <label class="form-label text-light-accent">Option 1</label>
              <input v-model="option1" class="form-control custom-input" required />
            </div>
            <div class="mb-2">
              <label class="form-label text-light-accent">Option 2</label>
              <input v-model="option2" class="form-control custom-input" required />
            </div>
            <div class="mb-2" v-if="questionText.length > 0"> <!-- Only show optional if question text exists -->
              <label class="form-label text-light-accent">Option 3 (Optional)</label>
              <input v-model="option3" class="form-control custom-input" />
            </div>
            <div class="mb-2" v-if="questionText.length > 0"> <!-- Only show optional if question text exists -->
              <label class="form-label text-light-accent">Option 4 (Optional)</label>
              <input v-model="option4" class="form-control custom-input" />
            </div>
            <div class="mb-2">
              <label class="form-label text-light-accent">Correct Option (1-4)</label>
              <input v-model.number="correctOption" type="number" class="form-control custom-input" required min="1" max="4" />
            </div>
            <button class="btn custom-btn-filled" type="submit">
              {{ editingQuestionId ? "Save Question Changes" : "Add Question" }}
            </button>
            <button v-if="editingQuestionId" class="btn custom-btn-outline ms-2" @click="cancelEditQuestion">Cancel</button>
            <button class="btn custom-btn-outline ms-2" @click="selectedQuizForQuestionsId = null">Back to Quizzes</button>
          </form>

          <!-- Questions List -->
          <h4 class="text-light-accent mb-3">Questions for "{{ quizTitleById(selectedQuizForQuestionsId) }}"</h4>
          <ul class="list-group custom-list-group">
            <li v-for="question in questions" :key="question.id" class="list-group-item d-flex justify-content-between align-items-center custom-list-item">
              <span>
                <b class="text-primary-neon">Q: {{ question.question_text }}</b>
                <br>
                <small class="text-light-accent">
                  1. {{ question.option1 }} <br>
                  2. {{ question.option2 }} <br>
                  <span v-if="question.option3">3. {{ question.option3 }} <br></span>
                  <span v-if="question.option4">4. {{ question.option4 }} <br></span>
                  Correct: Option {{ question.correct_option }}
                </small>
              </span>
              <div>
                <button class="btn btn-sm custom-icon-btn me-2" @click="editQuestion(question)">
                  <i class="bi bi-pencil-fill"></i>
                </button>
                <button class="btn btn-sm custom-icon-btn-danger" @click="deleteQuestion(question.id)">
                  <i class="bi bi-trash-fill"></i>
                </button>
              </div>
            </li>
            <li v-if="questions.length === 0" class="list-group-item custom-list-item text-center text-light-accent">No questions found for this quiz.</li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const subjects = ref([])
const chapters = ref([])
const quizzes = ref([])
const questions = ref([])

// Quiz form refs
const selectedSubjectId = ref('')
const selectedChapterId = ref('')
const quizTitle = ref('')
const quizDescription = ref('')
const quizDuration = ref(60)
const quizDate = ref(new Date().toISOString().slice(0, 10))
const editingQuizId = ref(null)
const searchQuizQuery = ref(''); // Search query for quizzes

// Question form refs
const selectedQuizForQuestionsId = ref(null)
const questionText = ref('')
const option1 = ref('')
const option2 = ref('')
const option3 = ref('')
const option4 = ref('')
const correctOption = ref(1)
const editingQuestionId = ref(null)

const filteredChapters = computed(() => {
  // Filters the 'chapters' array based on selectedSubjectId
  return chapters.value.filter(c => c.subject_id === Number(selectedSubjectId.value))
})

const quizTitleById = (id) => {
  const quiz = quizzes.value.find(q => q.id === Number(id))
  return quiz ? quiz.title : 'Selected Quiz'
}

const chapterName = (id) => {
  const chap = chapters.value.find(c => c.id === Number(id))
  return chap ? chap.name : ''
}

async function fetchSubjects(bypassCache = false) {
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    const url = new URL('http://localhost:5000/api/subjects');
    if (bypassCache) {
      url.searchParams.append('cache_bust', Date.now());
    }
    const response = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { subjects.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load subjects: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching subjects:', error); alert('Network error. Could not connect to the server.'); }
}

// MODIFIED: fetchChapters now accepts a search query and bypassCache
async function fetchChapters(subjectId, query = '', bypassCache = false) {
  if (!subjectId) { chapters.value = []; return; }
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    
    const url = new URL(`http://localhost:5000/api/subjects/${subjectId}/chapters`);
    if (query) {
      url.searchParams.append('query', query);
    }
    if (bypassCache) {
      url.searchParams.append('cache_bust', Date.now());
    }

    const response = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { chapters.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load chapters: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching chapters:', error); alert('Network error. Could not connect to the server.'); }
}

const fetchChaptersWithSearch = (bypassCache = false) => {
  fetchChapters(selectedSubjectId.value, '', bypassCache); // MODIFIED: Pass empty string for query, as this is for chapter dropdown
};

async function fetchQuizzes(chapterId, query = '', bypassCache = false) {
  if (!chapterId) { quizzes.value = []; return; }
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    
    const url = new URL(`http://localhost:5000/api/chapters/${chapterId}/quizzes`);
    if (query) {
      url.searchParams.append('query', query);
    }
    if (bypassCache) {
      url.searchParams.append('cache_bust', Date.now());
    }

    const response = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { quizzes.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load quizzes: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching quizzes:', error); alert('Network error. Could not connect to the server.'); }
}

const fetchQuizzesWithSearch = (bypassCache = false) => {
  fetchQuizzes(selectedChapterId.value, searchQuizQuery.value, bypassCache);
};

async function fetchQuestions(quizId, bypassCache = false) {
  if (!quizId) { questions.value = []; return; }
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    const url = new URL(`http://localhost:5000/api/quizzes/${quizId}/questions`);
    if (bypassCache) {
      url.searchParams.append('cache_bust', Date.now());
    }
    const response = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { questions.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load questions: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching questions:', error); alert('Network error. Could not connect to the server.'); }
}

onMounted(() => fetchSubjects());

watch(selectedSubjectId, (newSubjectId) => {
  fetchChaptersWithSearch(); // MODIFIED: Call fetchChaptersWithSearch without query for chapter dropdown
  selectedChapterId.value = '';
  quizzes.value = [];
  selectedQuizForQuestionsId.value = null;
  searchQuizQuery.value = ''; // Reset quiz search query
});

watch(selectedChapterId, (newChapterId) => {
  fetchQuizzesWithSearch();
  selectedQuizForQuestionsId.value = null;
});

watch(selectedQuizForQuestionsId, (newQuizId) => {
  if (newQuizId) {
    fetchQuestions(newQuizId);
  } else {
    questions.value = [];
  }
});

async function addQuiz() {
  if (!selectedChapterId.value) { alert('Please select a chapter first.'); return; }
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  const quizData = {
    chapter_id: Number(selectedChapterId.value),
    title: quizTitle.value,
    description: quizDescription.value,
    time_duration: Number(quizDuration.value),
    date_of_quiz: quizDate.value
  };

  const url = editingQuizId.value
    ? `http://localhost:5000/api/quizzes/${editingQuizId.value}`
    : `http://localhost:5000/api/chapters/${selectedChapterId.value}/quizzes`;

  const method = editingQuizId.value ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(quizData)
    });

    if (response.ok) {
      await fetchQuizzesWithSearch(true); // Force cache bypass after add/edit
      cancelEditQuiz();
    } else {
      const errorData = await response.json();
      alert(`Failed to ${editingQuizId.value ? 'update' : 'add'} quiz: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) { console.error('Network error in addQuiz:', error); alert('Network error. Could not connect to the server.'); }
}

function editQuiz(quiz) {
  editingQuizId.value = quiz.id;
  quizTitle.value = quiz.title;
  quizDescription.value = quiz.description;
  quizDuration.value = quiz.time_duration;
  quizDate.value = quiz.date_of_quiz;
}

async function deleteQuiz(id) {
  if (!confirm('Are you sure you want to delete this quiz? This action cannot be undone.')) { return; }
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const response = await fetch(`http://localhost:5000/api/quizzes/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      await fetchQuizzesWithSearch(true); // Force cache bypass after delete
      if (editingQuizId.value === id) { cancelEditQuiz(); }
      if (selectedQuizForQuestionsId.value === id) { selectedQuizForQuestionsId.value = null; }
    } else {
      const errorData = await response.json();
      alert(`Failed to delete quiz: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) { console.error('Network error in deleteQuiz:', error); alert('Network error. Could not connect to the server.'); }
}

function cancelEditQuiz() {
  editingQuizId.value = null;
  quizTitle.value = '';
  quizDescription.value = '';
  quizDuration.value = 60;
  quizDate.value = new Date().toISOString().slice(0, 10);
}

function selectQuizForQuestions(quiz) {
  selectedQuizForQuestionsId.value = quiz.id;
  cancelEditQuestion();
}

async function addQuestion() {
  if (!selectedQuizForQuestionsId.value) { alert('Please select a quiz to add questions to.'); return; }
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  const questionData = {
    quiz_id: Number(selectedQuizForQuestionsId.value),
    question_text: questionText.value,
    option1: option1.value,
    option2: option2.value,
    option3: option3.value || null,
    option4: option4.value || null,
    correct_option: Number(correctOption.value)
  };

  const url = editingQuestionId.value
    ? `http://localhost:5000/api/questions/${editingQuestionId.value}`
    : `http://localhost:5000/api/quizzes/${selectedQuizForQuestionsId.value}/questions`;

  const method = editingQuestionId.value ? 'PUT' : 'POST';

  try {
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(questionData)
    });

    if (response.ok) {
      await fetchQuestions(selectedQuizForQuestionsId.value, true); // Force cache bypass after add/edit
      cancelEditQuestion();
    } else {
      const errorData = await response.json();
      alert(`Failed to ${editingQuestionId.value ? 'update' : 'add'} question: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) { console.error('Network error in addQuestion:', error); alert('Network error. Could not connect to the server.'); }
}

function editQuestion(question) {
  editingQuestionId.value = question.id;
  questionText.value = question.question_text;
  option1.value = question.option1;
  option2.value = question.option2;
  option3.value = question.option3;
  option4.value = question.option4;
  correctOption.value = question.correct_option;
}

async function deleteQuestion(id) {
  if (!confirm('Are you sure you want to delete this question? This action cannot be undone.')) { return; }
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const response = await fetch(`http://localhost:5000/api/questions/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      await fetchQuestions(selectedQuizForQuestionsId.value, true); // Force cache bypass after delete
      if (editingQuestionId.value === id) { cancelEditQuestion(); }
    } else {
      const errorData = await response.json();
      alert(`Failed to delete question: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) { console.error('Network error in deleteQuestion:', error); alert('Network error. Could not connect to the server.'); }
}

function cancelEditQuestion() {
  editingQuestionId.value = null;
  questionText.value = '';
  option1.value = '';
  option2.value = '';
  option3.value = '';
  option4.value = '';
  correctOption.value = 1;
}

function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* No component-specific styles needed here if all are common and in admin.css */

/* Custom select dropdown styling (unique to this page) */
.custom-select {
  background-color: #3d2766; /* Darker input background */
  border: 1px solid #6a4a9c; /* Purple border */
  color: #e0e0e0; /* Light text in input */
  border-radius: 8px; /* Rounded input fields */
  padding: 10px 15px;
  appearance: none; /* Remove default select arrow */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='none' stroke='%23e060a8' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3E%3C/svg%3E"); /* Custom arrow */
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px 12px;
}
.custom-select:focus {
  border-color: #e060a8; /* Neon pink focus border */
  box-shadow: 0 0 0 0.25rem rgba(224, 96, 168, 0.25); /* Neon glow on focus */
}
</style>
