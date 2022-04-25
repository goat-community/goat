import Vue from "vue";
import Router from "vue-router";
import { validateToken } from "../utils/Helpers";
Vue.use(Router);

//Create routes
let router = new Router({
  mode: "history",
  routes: [
    {
      path: "/",
      name: "main",
      component: () => import("../views/Main.vue"),
      meta: {
        requiresAuth: true,
        scope: "user"
      }
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/Auth.vue"),
      meta: {
        requiresAuth: false
      }
    },
    {
      path: "/forgot-password",
      name: "forgot-password",
      component: () => import("../views/Auth.vue"),
      meta: {
        requiresAuth: false
      }
    },
    {
      path: "/reset-password",
      name: "reset-password",
      component: () => import("../views/Auth.vue"),
      meta: {
        requiresAuth: false
      }
    },
    {
      path: "/register",
      name: "register-demo",
      component: () => import("../views/Auth.vue"),
      meta: {
        requiresAuth: false
      }
    },
    {
      path: "/activate-account",
      name: "activate-account",
      component: () => import("../views/Auth.vue"),
      meta: {
        requiresAuth: false
      }
    }
  ]
});

// Ensure we checked auth before each page load.
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(x => x.meta.requiresAuth);
  if (!requiresAuth) {
    return next();
  }
  // Get roles and check if user is allowed
  const token = localStorage.getItem("id_token");
  const decodedToken = validateToken(token);
  if (!decodedToken) {
    return next({ path: "/login" });
  }
  return next();
});

export default router;
