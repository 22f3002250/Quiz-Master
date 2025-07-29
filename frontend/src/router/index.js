import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import DashboardView from '../views/DashboardView.vue';
import AdminDashboardView from '../views/AdminDashboardView.vue';
import AdminSubjectsView from '../views/AdminSubjectsView.vue';
import AdminChaptersView from '../views/AdminChaptersView.vue';
import AdminQuizzesView from '../views/AdminQuizzesView.vue';
import AdminUsersView from '../views/AdminUsersView.vue';
import AdminReportsView from '../views/AdminReportsView.vue';
import QuizzesView from '../views/QuizzesView.vue';
import ScoresView from '../views/ScoresView.vue';
import ProfileView from '../views/ProfileView.vue';

// Create the router instance and define routes

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: '/', name: 'home', component: Home },
        { path: '/login', name: 'login', component: LoginView },
        { path: '/register', name: 'register', component: RegisterView },
        { path: '/dashboard', name: 'dashboard', component: DashboardView },
        { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboardView },
        { path: '/admin/subjects', component: AdminSubjectsView },
        { path: '/admin/chapters', component: AdminChaptersView, meta: { requiresAuth: true, role: 'admin' } },
        { path: '/admin/quizzes', component: AdminQuizzesView, meta: { requiresAuth: true, role: 'admin' } },
        { path: '/admin/users', component: AdminUsersView, meta: { requiresAuth: true, role: 'admin' } },
        { path: '/admin/reports', component: AdminReportsView },
        { path: '/quizzes', name: 'quizzes', component: QuizzesView, meta: { requiresAuth: true, role: 'user' } },
        { path: '/scores', name: 'scores', component: ScoresView, meta: { requiresAuth: true, role: 'user' } },
        { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true, role: 'user' } },
    ]
});

export default router;