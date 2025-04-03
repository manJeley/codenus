import {createRouter, createWebHistory} from 'vue-router'
import {role} from './guards.js'

import template from '../layouts/admin.vue'

/* {{place new import}} */
const notFound = () => import('../views/notFound.vue')

const base = () => import('../views/dashboard.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: template,
      beforeEnter: (to, from, next) => {
        role(to, from, next)
      },
      children: [
        {path: '', name: 'base', component: base},
        /* {{place new app route}} */
      ]
    },
    /* {{place new route}} */
    {
      path: '/',
      component: template,
      beforeEnter: (to, from, next) => {
        role(to, from, next)
      },
      children: [
        {path: '/:pathMatch(.*)*', name: 'not_found', component: notFound}
      ]
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    return new Promise((resolve) => {
      if (savedPosition) {
        return resolve(savedPosition)
      }
      resolve({behavior: 'smooth', left: 0, top: 0})
    })
  }
})

export default router
