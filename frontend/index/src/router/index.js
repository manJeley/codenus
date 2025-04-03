import { createRouter, createWebHistory } from 'vue-router'

import { auth, profile_complete } from '@/router/guards.js'
import IndexLayout from '../layouts/home.vue'
import UserLayout from '../layouts/user.vue'
const base = () => import('../views/home.vue')
const notFound = () => import('../views/notFound.vue')

const dashboard = () => import('../views/user/index.vue')

function getLangsCookie() {
  let name = 'langs='
  let decodedCookie = decodeURIComponent(document.cookie)
  let ca = decodedCookie.split(';')
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) === ' ') {
      c = c.substring(1)
    }
    if (c.indexOf(name) === 0) {
      return c.substring(name.length, c.length)
    }
  }
  return ''
}

function update_routes(routes) {
  let lang = localStorage.getItem('lang')
  if (!lang) {
    lang = 'en'
  } else {
    lang = JSON.parse(lang)
  }
  let p = window.location.pathname.split('/')
  let siteDefault = localStorage.getItem('siteDefault')
  let langs = ['en']
  if (siteDefault) {
    langs = Object.keys(JSON.parse(siteDefault)['langs'])
  } else {
    let l = getLangsCookie()
    if (l) {
      langs = l.split(',')
    }
  }
  if (p[1] !== lang) {
    if (langs.includes(p[1])) {
      localStorage.setItem('lang', JSON.stringify(p[1]))
      lang = p[1]
    }
  }

  routes.forEach((r) => {
    if (r.path.startsWith('/')) {
      r.path = '/' + lang + r.path
    } else {
      r.path = lang + '/' + r.path
    }
  })
  return routes
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: update_routes([
    {
      path: '/',
      component: IndexLayout,
      children: [
        { path: '', name: 'base', component: base },
        {
          path: '/user',
          component: UserLayout,
          beforeEnter: (to, from, next) => {
            auth(to, from, next)
          },
          children: [
            {
              path: '', name: 'dashboard', component: dashboard, beforeEnter: (to, from, next) => {
                profile_complete(to, from, next)
              }
            }
          ]
        }
      ]
    },
    /* {{place new route}} */
    {
      path: '/',
      component: IndexLayout,
      children: [
        { path: '/:pathMatch(.*)*', name: 'not_found', component: notFound }
      ]
    }
  ]),
  scrollBehavior(to, from, savedPosition) {
    return new Promise((resolve) => {
      if (savedPosition) {
        setTimeout(() => {
          resolve({ left: 0, top: savedPosition['top'] })
        }, 500)
      } else {
        resolve({ left: 0, top: 0 })
      }
    })
  }
})

router.beforeEach((to, from, next) => {
  if (to.path === '/') {
    next({ name: 'base' })
  } else {
    next()
  }
})
export default router
