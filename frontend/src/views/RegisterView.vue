<template>
  <div class="register-container d-flex justify-content-center align-items-center">
    <div class="card p-4 shadow-lg rounded-3 register-card">
      <h2 class="mb-4 text-center text-primary-neon">Register</h2>
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="email" class="form-label text-light-accent">Email</label>
          <input v-model="email" type="email" class="form-control custom-input" id="email" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label text-light-accent">Password</label>
          <input v-model="password" type="password" class="form-control custom-input" id="password" required />
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
        <button type="submit" class="btn btn-primary w-100 custom-btn-filled" :disabled="loading">
          {{ loading ? "Registering..." : "Register" }}
        </button>
        <div v-if="error" class="alert alert-danger mt-3 custom-alert">{{ error }}</div>
      </form>
      <div class="text-center mt-3">
        <router-link to="/login" class="text-link-neon">Already have an account? Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const full_name = ref('')
const qualification = ref('')
const dob = ref('') // YYYY-MM-DD format for input type="date"
const loading = ref(false)
const error = ref('')
const router = useRouter()

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('http://localhost:5000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        full_name: full_name.value,
        qualification: qualification.value,
        dob: dob.value // Send as YYYY-MM-DD string
      })
    })
    const data = await response.json()
    if (response.ok) {
      alert('Registration successful! Please login.')
      router.push('/login')
    } else {
      error.value = data.message || 'Registration failed'
    }
  } catch (err) {
    error.value = 'Network error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #1a0f2d; /* Dark purple background */
  padding: 20px;
}

.register-card {
  max-width: 500px; /* Slightly wider card for more fields */
  width: 100%;
  background-color: #2b1a47; /* Darker card background */
  border: 1px solid #4a2d73; /* Subtle border */
  border-radius: 15px; /* More rounded corners */
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5); /* Deeper shadow */
}

.text-primary-neon {
  color: #e060a8; /* Neon pink for headings */
  text-shadow: 0 0 8px rgba(224, 96, 168, 0.7); /* Neon glow */
  font-weight: bold;
}

.text-light-accent {
  color: #c0b0d0; /* Lighter text for labels */
}

.custom-input {
  background-color: #3d2766; /* Darker input background */
  border: 1px solid #6a4a9c; /* Purple border */
  color: #e0e0e0; /* Light text in input */
  border-radius: 8px; /* Rounded input fields */
  padding: 10px 15px;
}
.custom-input:focus {
  background-color: #4a307a;
  border-color: #e060a8; /* Neon pink focus border */
  box-shadow: 0 0 0 0.25rem rgba(224, 96, 168, 0.25); /* Neon glow on focus */
  color: #e0e0e0;
}

.custom-btn-filled {
  background-color: #8a2be2; /* Blue-violet for filled button */
  border-color: #8a2be2;
  border-radius: 10px; /* Rounded button */
  font-weight: bold;
  padding: 10px 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(138, 43, 226, 0.4); /* Glow effect */
}
.custom-btn-filled:hover {
  background-color: #7a1ee0;
  border-color: #7a1ee0;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(138, 43, 226, 0.6);
}

.text-link-neon {
  color: #5dbeff; /* Electric blue for links */
  text-decoration: none;
  transition: color 0.3s ease;
}
.text-link-neon:hover {
  color: #2a9dff;
  text-decoration: underline;
}

.custom-alert {
  background-color: #4a1a1a; /* Dark red for alerts */
  color: #ff8080; /* Light red text */
  border-color: #802020;
  border-radius: 8px;
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .register-card {
    padding: 1.5rem !important;
  }
  .h2 {
    font-size: 1.8rem;
  }
}
</style>
