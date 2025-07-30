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
        <h2 class="mb-4 text-center text-primary-neon">Attempt Quizzes</h2>

        <!-- Select Subject and Chapter for Quiz -->
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

        <!-- List of Quizzes to Attempt -->
        <h4 v-if="selectedChapterId" class="text-light-accent mb-3">Available Quizzes for {{ chapterName(selectedChapterId) }}</h4>
        <ul class="list-group custom-list-group" v-if="selectedChapterId && quizzes.length > 0">
          <li v-for="quiz in quizzes" :key="quiz.id" class="list-group-item d-flex justify-content-between align-items-center custom-list-item">
            <span>
              <b class="text-primary-neon">{{ quiz.title }}</b> - <span class="text-light-accent">{{ quiz.description }}</span>
              <br>
              <small class="text-light-accent">Duration: {{ quiz.time_duration }} mins | Date: {{ quiz.date_of_quiz }}</small>
            </span>
            <div>
              <button class="btn btn-sm custom-btn-filled" @click="startQuiz(quiz)">Start Quiz</button>
            </div>
          </li>
        </ul>
        <div v-else-if="selectedChapterId" class="alert alert-info mt-3 custom-alert">No quizzes available for this chapter.</div>
        <div v-else class="alert alert-info mt-3 custom-alert">Please select a subject and chapter to view quizzes.</div>

        <!-- Quiz Attempt Section -->
        <div v-if="currentQuiz && !quizCompleted" class="mt-5">
          <h3 class="text-primary-neon text-center mb-4">Quiz: "{{ currentQuiz.title }}"</h3>
          <p class="text-center text-light-accent">Time Remaining: {{ formatTime(timeRemaining) }}</p>

          <div v-if="currentQuestion">
            <div class="card p-4 mb-4 custom-list-item">
              <p class="text-light-accent fs-5 mb-3">Q: {{ currentQuestion.question_text }}</p>
              <div class="form-check mb-2">
                <input class="form-check-input custom-radio" type="radio" :name="'question-' + currentQuestion.id" :id="'option1-' + currentQuestion.id" :value="1" v-model="selectedOption" />
                <label class="form-check-label text-light-accent" :for="'option1-' + currentQuestion.id">{{ currentQuestion.option1 }}</label>
              </div>
              <div class="form-check mb-2">
                <input class="form-check-input custom-radio" type="radio" :name="'question-' + currentQuestion.id" :id="'option2-' + currentQuestion.id" :value="2" v-model="selectedOption" />
                <label class="form-check-label text-light-accent" :for="'option2-' + currentQuestion.id">{{ currentQuestion.option2 }}</label>
              </div>
              <div class="form-check mb-2" v-if="currentQuestion.option3">
                <input class="form-check-input custom-radio" type="radio" :name="'question-' + currentQuestion.id" :id="'option3-' + currentQuestion.id" :value="3" v-model="selectedOption" />
                <label class="form-check-label text-light-accent" :for="'option3-' + currentQuestion.id">{{ currentQuestion.option3 }}</label>
              </div>
              <div class="form-check mb-2" v-if="currentQuestion.option4">
                <input class="form-check-input custom-radio" type="radio" :name="'question-' + currentQuestion.id" :id="'option4-' + currentQuestion.id" :value="4" v-model="selectedOption" />
                <label class="form-check-label text-light-accent" :for="'option4-' + currentQuestion.id">{{ currentQuestion.option4 }}</label>
              </div>
            </div>
            <div class="d-flex justify-content-between mt-4">
              <!-- MODIFIED: Previous button color -->
              <button class="btn custom-btn-pink-outline" @click="previousQuestion" :disabled="currentQuestionIndex === 0">Previous</button>
              <!-- MODIFIED: Next button color -->
              <button class="btn custom-btn-green-filled" @click="nextQuestion" :disabled="currentQuestionIndex === (quizQuestions.length - 1)">Next</button>
              <button class="btn custom-btn-danger" @click="submitQuiz">Submit Quiz</button>
            </div>
          </div>
          <div v-else class="text-center text-light-accent">Loading questions...</div>
        </div>

        <!-- Quiz Completed Section -->
        <div v-if="quizCompleted" class="mt-5 text-center">
          <h3 class="text-primary-neon mb-4">Quiz Completed!</h3>
          <p class="text-light-accent fs-5">Your Score: {{ finalScore }} / {{ quizQuestions.length }}</p>
          <p class="text-light-accent">Correct Answers: {{ correctAnswersCount }}</p>
          <button class="btn custom-btn-filled mt-3" @click="resetQuizAttempt">Attempt Another Quiz</button>
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
const quizQuestions = ref([]) // Stores questions for the current quiz attempt

// Quiz selection and attempt state
const selectedSubjectId = ref('')
const selectedChapterId = ref('')
const currentQuiz = ref(null)
const currentQuestionIndex = ref(0)
const currentQuestion = computed(() => quizQuestions.value[currentQuestionIndex.value])
const userAnswers = ref({}) // Stores user's selected options: { questionId: selectedOption }
const timeRemaining = ref(0)
let timerInterval = null
const quizCompleted = ref(false)
const finalScore = ref(0)
const correctAnswersCount = ref(0)

// --- Computed Properties ---
const filteredChapters = computed(() => {
  return chapters.value.filter(c => c.subject_id === Number(selectedSubjectId.value))
})

const chapterName = (id) => {
  const chap = chapters.value.find(c => c.id === Number(id))
  return chap ? chap.name : ''
}

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}

// --- Fetching Functions ---
async function fetchSubjects() {
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    // MODIFIED: Use new user-accessible endpoint
    const response = await fetch('http://localhost:5000/api/user/subjects', {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { subjects.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load subjects: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching subjects:', error); alert('Network error. Could not connect to the server.'); }
}

async function fetchChapters(subjectId) {
  if (!subjectId) { chapters.value = []; return; }
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    // MODIFIED: Use new user-accessible endpoint
    const response = await fetch(`http://localhost:5000/api/user/subjects/${subjectId}/chapters`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { chapters.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load chapters: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching chapters:', error); alert('Network error. Could not connect to the server.'); }
}

async function fetchQuizzes(chapterId) {
  if (!chapterId) { quizzes.value = []; return; }
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    // MODIFIED: Use new user-accessible endpoint
    const response = await fetch(`http://localhost:5000/api/user/chapters/${chapterId}/quizzes`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { quizzes.value = await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load quizzes: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching quizzes:', error); alert('Network error. Could not connect to the server.'); }
}

async function fetchQuestionsForQuiz(quizId) {
  try {
    const token = localStorage.getItem('token');
    if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }
    // MODIFIED: Use new user-accessible endpoint
    const response = await fetch(`http://localhost:5000/api/user/quizzes/${quizId}/questions`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (response.ok) { return await response.json(); }
    else { const errorData = await response.json(); alert(`Failed to load questions: ${errorData.message || response.statusText}`); if (response.status === 401 || response.status === 403) { router.push('/login'); } }
  } catch (error) { console.error('Network error fetching questions:', error); alert('Network error. Could not connect to the server.'); }
  return [];
}

// --- Quiz Attempt Logic ---
async function startQuiz(quiz) {
  currentQuiz.value = quiz;
  quizQuestions.value = await fetchQuestionsForQuiz(quiz.id);
  userAnswers.value = {}; // Reset answers for new quiz
  currentQuestionIndex.value = 0;
  quizCompleted.value = false;
  finalScore.value = 0;
  correctAnswersCount.value = 0;

  // Initialize time remaining and start timer
  timeRemaining.value = quiz.time_duration * 60; // Convert minutes to seconds
  clearInterval(timerInterval); // Clear any existing timer
  timerInterval = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--;
    } else {
      clearInterval(timerInterval);
      submitQuiz(); // Auto-submit when time runs out
    }
  }, 1000);

  // Pre-select user's previous answer if available
  if (currentQuestion.value && userAnswers.value[currentQuestion.value.id]) {
    selectedOption.value = userAnswers.value[currentQuestion.value.id];
  } else {
    selectedOption.value = null;
  }
}

function nextQuestion() {
  // Save current answer
  if (currentQuestion.value && selectedOption.value !== null) {
    userAnswers.value[currentQuestion.value.id] = selectedOption.value;
  }

  if (currentQuestionIndex.value < quizQuestions.value.length - 1) {
    currentQuestionIndex.value++;
    // Load next question's answer
    selectedOption.value = userAnswers.value[currentQuestion.value.id] || null;
  }
}

function previousQuestion() {
  // Save current answer
  if (currentQuestion.value && selectedOption.value !== null) {
    userAnswers.value[currentQuestion.value.id] = selectedOption.value;
  }

  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
    // Load previous question's answer
    selectedOption.value = userAnswers.value[currentQuestion.value.id] || null;
  }
}

async function submitQuiz() {
  clearInterval(timerInterval); // Stop the timer

  // Ensure last question's answer is saved
  if (currentQuestion.value && selectedOption.value !== null) {
    userAnswers.value[currentQuestion.value.id] = selectedOption.value;
  }

  const answersToSubmit = [];
  for (const q of quizQuestions.value) {
    const userAnswer = userAnswers.value[q.id];
    answersToSubmit.push({
      question_id: q.id,
      selected_option: userAnswer || 0 // Store 0 if not answered
    });
  }

  // Submit score and individual answers to backend
  const result = await saveQuizResults(currentQuiz.value.id, answersToSubmit);

  if (result && result.final_score !== undefined) {
    finalScore.value = result.final_score;
    correctAnswersCount.value = result.correct_answers_count;
  } else {
    finalScore.value = 0; // Default to 0 if backend result is missing
    correctAnswersCount.value = 0;
  }
  quizCompleted.value = true;
}

async function saveQuizResults(quizId, answers) {
  const token = localStorage.getItem('token');
  if (!token) { alert('Authentication token missing. Please log in.'); router.push('/login'); return; }

  try {
    const response = await fetch('http://localhost:5000/api/quiz_attempt_submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ quiz_id: quizId, answers: answers })
    });

    if (response.ok) {
      const resultData = await response.json();
      alert(resultData.message);
      return resultData; // Return data including final_score and correct_answers_count
    } else {
      const errorData = await response.json();
      alert(`Failed to submit quiz: ${errorData.message || response.statusText}`);
      if (response.status === 401 || response.status === 403) { router.push('/login'); }
    }
  } catch (error) {
    console.error('Network error saving quiz results:', error);
    alert('Network error. Could not connect to the server when saving results.');
  }
  return null;
}


function resetQuizAttempt() {
  currentQuiz.value = null;
  quizQuestions.value = [];
  userAnswers.value = {};
  currentQuestionIndex.value = 0;
  quizCompleted.value = false;
  finalScore.value = 0;
  correctAnswersCount.value = 0;
  timeRemaining.value = 0;
  clearInterval(timerInterval);
  selectedOption.value = null; // Clear selected option
}

const selectedOption = ref(null) // For radio button binding

// --- Lifecycle Hooks and Watchers ---
onMounted(fetchSubjects);

watch(selectedSubjectId, (newSubjectId) => {
  fetchChapters(newSubjectId);
  selectedChapterId.value = '';
  quizzes.value = [];
  resetQuizAttempt(); // Reset quiz state when subject changes
});

watch(selectedChapterId, (newChapterId) => {
  fetchQuizzes(newChapterId);
  resetQuizAttempt(); // Reset quiz state when chapter changes
});

watch(currentQuestionIndex, (newIndex) => {
  if (currentQuestion.value) { // Ensure currentQuestion is not null
    selectedOption.value = userAnswers.value[currentQuestion.value.id] || null;
  }
});


// --- Logout Function ---
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* All common styles for user layout and content are in user.css */

/* Custom radio button styling */
.custom-radio {
  background-color: #3d2766; /* Darker background */
  border: 1px solid #6a4a9c; /* Purple border */
  border-radius: 50%; /* Make it round */
  width: 1.25rem;
  height: 1.25rem;
  appearance: none; /* Remove default radio button style */
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  top: 0.2em; /* Adjust vertical alignment */
}
.custom-radio:checked {
  background-color: #e060a8; /* Neon pink when checked */
  border-color: #e060a8;
  box-shadow: 0 0 0 0.25rem rgba(224, 96, 168, 0.25); /* Neon glow */
}
.custom-radio:focus {
  outline: none;
  box-shadow: 0 0 0 0.25rem rgba(224, 96, 168, 0.5);
}
.custom-radio:checked::after {
  content: '';
  display: block;
  width: 0.5rem;
  height: 0.5rem;
  background-color: #1a0f2d; /* Dark center dot */
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>