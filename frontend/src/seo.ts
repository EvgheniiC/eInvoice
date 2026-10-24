import { publicPageByPath, type PublicPage } from './content/publicPages'

export const SITE_ORIGIN: string = 'https://erechnung-smart.de'
export const SITE_NAME: string = 'eInvoice'

export type SeoRobots = 'index,follow' | 'noindex,nofollow'

export type SeoPage = {
  title: string
  description: string
  canonicalPath: string
  robots: SeoRobots
}

const HOME_PAGE: PublicPage = requiredPublicPage('/')

export const LANDING_HEADLINE: string = HOME_PAGE.h1
export const LANDING_DESCRIPTION: string = HOME_PAGE.description

const DEFAULT_DESCRIPTION: string = LANDING_DESCRIPTION

const LANDING: SeoPage = {
  title: HOME_PAGE.title,
  description: HOME_PAGE.description,
  canonicalPath: '/',
  robots: 'index,follow',
}

function normalizePath(pathname: string): string {
  const trimmed: string = pathname.replace(/\/+$/, '')
  return trimmed === '' ? '/' : trimmed
}

function requiredPublicPage(path: string): PublicPage {
  const page: PublicPage | null = publicPageByPath(path)
  if (page === null) {
    throw new Error(`Missing public page: ${path}`)
  }
  return page
}

function pageSeo(page: PublicPage, canonicalPath: string = page.path): SeoPage {
  return {
    title: page.title,
    description: page.description,
    canonicalPath,
    robots: 'index,follow',
  }
}

export function seoForPath(pathname: string): SeoPage {
  const path: string = normalizePath(pathname)

  if (path === '/faq') {
    return pageSeo(requiredPublicPage('/hilfe'), '/hilfe')
  }

  const published: PublicPage | null = publicPageByPath(path)
  if (published !== null) {
    return pageSeo(published)
  }
  if (path === '/anmelden') {
    return noIndexPage('Anmelden | eInvoice', '/anmelden')
  }
  if (path === '/registrieren') {
    return noIndexPage('Registrieren | eInvoice', '/registrieren')
  }
  if (path === '/passwort-vergessen') {
    return noIndexPage('Passwort vergessen | eInvoice', '/passwort-vergessen')
  }
  if (path === '/passwort-zuruecksetzen') {
    return noIndexPage('Passwort zurücksetzen | eInvoice', '/passwort-zuruecksetzen')
  }
  if (path === '/bestaetigen') {
    return noIndexPage('E-Mail bestätigen | eInvoice', '/bestaetigen')
  }
  if (path === '/organisation') {
    return noIndexPage('Organisation | eInvoice', '/organisation')
  }
  if (path === '/verlauf') {
    return noIndexPage('Verlauf | eInvoice', '/verlauf')
  }
  if (path === '/statistik') {
    return noIndexPage('Statistik | eInvoice', '/statistik')
  }

  return LANDING
}

export function applySeo(pathname: string): void {
  const page: SeoPage = seoForPath(pathname)
  const canonicalUrl: string = `${SITE_ORIGIN}${page.canonicalPath}`

  document.title = page.title
  setMetaByName('description', page.description)
  setMetaByName('robots', page.robots)
  setLinkRel('canonical', canonicalUrl)
  setMetaByProperty('og:title', page.title)
  setMetaByProperty('og:description', page.description)
  setMetaByProperty('og:url', canonicalUrl)
}

function noIndexPage(title: string, canonicalPath: string): SeoPage {
  return {
    title,
    description: DEFAULT_DESCRIPTION,
    canonicalPath,
    robots: 'noindex,nofollow',
  }
}

function setMetaByName(name: string, content: string): void {
  let element: HTMLMetaElement | null = document.head.querySelector(`meta[name="${name}"]`)
  if (element === null) {
    element = document.createElement('meta')
    element.setAttribute('name', name)
    document.head.appendChild(element)
  }
  element.setAttribute('content', content)
}

function setMetaByProperty(property: string, content: string): void {
  let element: HTMLMetaElement | null = document.head.querySelector(
    `meta[property="${property}"]`,
  )
  if (element === null) {
    element = document.createElement('meta')
    element.setAttribute('property', property)
    document.head.appendChild(element)
  }
  element.setAttribute('content', content)
}

function setLinkRel(rel: string, href: string): void {
  let element: HTMLLinkElement | null = document.head.querySelector(`link[rel="${rel}"]`)
  if (element === null) {
    element = document.createElement('link')
    element.setAttribute('rel', rel)
    document.head.appendChild(element)
  }
  element.setAttribute('href', href)
}
