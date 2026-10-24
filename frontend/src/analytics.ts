export const GA_MEASUREMENT_ID: string = 'G-F7HBEYLZ0R'
export const CONSENT_STORAGE_KEY: string = 'einv_analytics_consent'

declare global {
  interface Window {
    dataLayer?: unknown[]
    gtag?: (...args: unknown[]) => void
  }
}

export type AnalyticsConsent = 'granted' | 'denied'

const ACCOUNT_PREFIXES: readonly string[] = [
  '/anmelden',
  '/registrieren',
  '/passwort-vergessen',
  '/passwort-zuruecksetzen',
  '/bestaetigen',
  '/organisation',
  '/verlauf',
  '/statistik',
]

const SENSITIVE_QUERY_KEYS: readonly string[] = ['token', 'session', 'code']

type ConsentListener = () => void

const consentListeners: Set<ConsentListener> = new Set()
let promptRequested: boolean = false
let tagInstalled: boolean = false
let lastTrackedKey: string = ''
let lastTrackedAt: number = 0

function notifyConsent(): void {
  for (const listener of consentListeners) {
    listener()
  }
}

function normalizePath(pathname: string): string {
  const trimmed: string = pathname.replace(/\/+$/, '')
  return trimmed === '' ? '/' : trimmed
}

function gtag(...args: unknown[]): void {
  window.dataLayer = window.dataLayer ?? []
  window.dataLayer.push(args)
}

function measurementCookieSuffix(): string {
  return GA_MEASUREMENT_ID.replace(/^G-/, '')
}

function expireCookie(name: string): void {
  const expires: string = 'Thu, 01 Jan 1970 00:00:00 GMT'
  document.cookie = `${name}=; expires=${expires}; path=/`
  const host: string = window.location.hostname
  if (host.includes('.')) {
    document.cookie = `${name}=; expires=${expires}; path=/; domain=.${host}`
  }
}

export function readAnalyticsConsent(): AnalyticsConsent | null {
  const stored: string | null = localStorage.getItem(CONSENT_STORAGE_KEY)
  if (stored === 'granted' || stored === 'denied') {
    return stored
  }
  return null
}

export function consentPromptRequested(): boolean {
  return promptRequested
}

export function subscribeAnalyticsConsent(listener: ConsentListener): () => void {
  consentListeners.add(listener)
  return (): void => {
    consentListeners.delete(listener)
  }
}

export function openAnalyticsConsentPrompt(): void {
  promptRequested = true
  notifyConsent()
}

export function isTrackableLocation(pathname: string, search: string): boolean {
  const path: string = normalizePath(pathname)
  const isAccount: boolean = ACCOUNT_PREFIXES.some(
    (prefix: string): boolean => path === prefix || path.startsWith(`${prefix}/`),
  )
  if (isAccount) {
    return false
  }
  const params: URLSearchParams = new URLSearchParams(search.startsWith('?') ? search.slice(1) : search)
  return !SENSITIVE_QUERY_KEYS.some((key: string): boolean => params.has(key))
}

function installGoogleTag(): void {
  if (tagInstalled || document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`) !== null) {
    tagInstalled = true
    return
  }
  tagInstalled = true
  window.dataLayer = window.dataLayer ?? []
  window.gtag = gtag
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'granted',
  })
  gtag('js', new Date())
  gtag('config', GA_MEASUREMENT_ID, {
    send_page_view: false,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
  })
  const script: HTMLScriptElement = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`
  script.dataset.ga = GA_MEASUREMENT_ID
  document.head.appendChild(script)
}

function stopGoogleTag(): void {
  window.gtag?.('consent', 'update', { analytics_storage: 'denied' })
  expireCookie('_ga')
  expireCookie('_gid')
  expireCookie(`_ga_${measurementCookieSuffix()}`)
}

export function trackPublicPage(pathname: string, search: string = window.location.search): void {
  if (readAnalyticsConsent() !== 'granted' || !isTrackableLocation(pathname, search)) {
    return
  }
  const path: string = normalizePath(pathname)
  const now: number = Date.now()
  if (lastTrackedKey === path && now - lastTrackedAt < 400) {
    return
  }
  lastTrackedKey = path
  lastTrackedAt = now
  installGoogleTag()
  window.gtag?.('consent', 'update', { analytics_storage: 'granted' })
  window.gtag?.('event', 'page_view', {
    page_path: path,
    page_location: `${window.location.origin}${path}`,
    page_title: document.title,
  })
}

export function saveAnalyticsConsent(choice: AnalyticsConsent, pathname: string, search: string): void {
  localStorage.setItem(CONSENT_STORAGE_KEY, choice)
  promptRequested = false
  if (choice === 'granted') {
    trackPublicPage(pathname, search)
  } else {
    lastTrackedKey = ''
    stopGoogleTag()
  }
  notifyConsent()
}

export function resetAnalyticsState(): void {
  promptRequested = false
  tagInstalled = false
  lastTrackedKey = ''
  lastTrackedAt = 0
  delete window.gtag
  delete window.dataLayer
}
