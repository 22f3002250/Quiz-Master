<template>
  <div class="main-wrapper">
    <!-- Left Section: Image Only -->
    <div class="left-image-section">
      <!-- The background image is applied via CSS to this div -->
    </div>

    <!-- Right Section: Content Only -->
    <div class="right-content-section d-flex flex-column justify-content-center align-items-center">
      <div class="card p-5 shadow-lg rounded-3 text-center hero-card">
        <h1 class="display-3 fw-bold mb-4 text-primary">QUIZ Practice</h1>
        <p class="lead mb-5 text-secondary">
          Welcome to the Quiz Practice platform! Here you can test your knowledge and improve your skills with a variety of quizzes.
          <br>
          <strong>Login or Register to get started!</strong>
        </p>
        <div class="d-flex justify-content-center gap-3 mb-5">
          <!-- Login Button -->
          <router-link to="/login" class="btn btn-outline-primary btn-lg px-4 py-2 rounded-pill fw-bold custom-btn">
            LOGIN
          </router-link>
          <!-- Register Button -->
          <router-link to="/register" class="btn btn-primary btn-lg px-4 py-2 rounded-pill fw-bold custom-btn">
            REGISTER
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No script logic needed for now, as the image is handled purely in CSS
</script>

<style scoped>
.main-wrapper {
  display: flex; /* Use flexbox for the two-column layout */
  min-height: 100vh; /* Ensure it takes full viewport height */
  width: 100%; /* Take full width */
  background-color:#141028; /* Fallback background for the whole page */
}

.left-image-section {
  flex: 1; /* Takes equal space as the right section on larger screens */
  background-image: url('/image1.jpeg'); /* Absolute path from public folder */
  background-size: leftover; /* Cover the entire section */
  background-position: center left; /* Position the image to the left within its section */
  background-repeat: no-repeat; /* Do not repeat */
  background-attachment: fixed; /* Keep background fixed when scrolling (optional) */
  min-height: 100vh; /* Ensure it takes full height */
}

.right-content-section {
  flex: 1; /* Takes equal space as the left section on larger screens */
  display: flex; /* Use flexbox to center content vertically and horizontally within this section */
  flex-direction: column;
  justify-content: center; /* Center content vertically */
  align-items: center; /* Center content horizontally */

}

.hero-card {
  background-color: #141028; /* Card background is white */
  border: none;
}

.display-3 {
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #e9bee9; /* Changed to primary blue for "QUIZ" title */
}

.lead {
  font-size: 1.25rem;
  color: #e0d0d2; /* Muted text color */
}

.custom-btn {
  min-width: 150px; /* Ensure buttons have a consistent width */
  border-radius: 50px; /* More rounded pills */
  font-size: 1.1rem;
  padding: 0.8rem 1.5rem;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #c643ac;
  border-color: #c643ac;
}
.btn-primary:hover {
  background-color: #b30065;
  border-color: #b30065;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(179, 0, 101, 0.3);
}

.btn-outline-primary {
  color: #c643ac;
  border-color: #c643ac;
  background-color: transparent;
}
.btn-outline-primary:hover {
  background-color: #c643ac;
  border-color: #c643ac;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(179, 0, 101, 0.3);
}

/* Ensure text colors are applied correctly */
.text-primary { color: #c264ab !important; }
.text-secondary { color: #8787ce !important; }
.text-muted { color: #d5d1d1 !important; }

/* Responsive adjustments */
@media (max-width: 992px) { /* Adjust breakpoint for stacking */
  .main-wrapper {
    flex-direction: column; /* Stack columns vertically on smaller screens */
  }
  .left-image-section {
    min-height: 300px; /* Give a fixed height to the image section when stacked */
    flex: none; 
    width: 100%;
  }
  .right-content-section {
    flex: none; /* Remove flex grow when stacked */
    width: 100%;
    padding: 30px 20px; /* Adjust padding when stacked */
  }
  .hero-card {
    max-width: 100%; /* Allow card to take full width of its section */
  }
}

@media (max-width: 768px) {
  .hero-card {
    padding: 2rem !important;
  }
  .display-3 {
    font-size: 2.5rem;
  }
  .lead {
    font-size: 1rem;
  }
  .custom-btn {
    min-width: 120px;
    font-size: 1rem;
    padding: 0.6rem 1rem;
  }
}

@media (max-width: 576px) {
  .hero-card {
    padding: 1.5rem !important;
  }
  .display-3 {
    font-size: 2rem;
  }
  .lead {
    font-size: 0.9rem;
  }
  .custom-btn {
    min-width: 100px;
    font-size: 0.9rem;
    padding: 0.5rem 0.8rem;
  }
}
</style>
