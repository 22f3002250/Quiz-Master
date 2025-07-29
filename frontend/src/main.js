import { createApp } from 'vue';
import './assets/admin.css';
import './assets/user.css';
import App from './App.vue';
import router from './router';

const app = createApp(App);
app.use(router);
app.mount('#app');