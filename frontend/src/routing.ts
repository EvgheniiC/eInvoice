export type AppRoute =
  | 'landing'
  | 'upload'
  | 'legal'
  | 'help'
  | 'login'
  | 'register'
  | 'forgot'
  | 'reset'
  | 'verify'
  | 'org'
  | 'history'

export function pathToRoute(pathname: string): AppRoute {
  if (pathname === '/upload' || pathname.startsWith('/upload/')) {
    return 'upload'
  }
  if (
    pathname === '/impressum' ||
    pathname.startsWith('/impressum/') ||
    pathname === '/datenschutz' ||
    pathname.startsWith('/datenschutz/')
  ) {
    return 'legal'
  }
  if (
    pathname === '/hilfe' ||
    pathname.startsWith('/hilfe/') ||
    pathname === '/faq' ||
    pathname.startsWith('/faq/')
  ) {
    return 'help'
  }
  if (pathname === '/anmelden' || pathname.startsWith('/anmelden/')) {
    return 'login'
  }
  if (pathname === '/registrieren' || pathname.startsWith('/registrieren/')) {
    return 'register'
  }
  if (pathname === '/passwort-vergessen' || pathname.startsWith('/passwort-vergessen/')) {
    return 'forgot'
  }
  if (pathname === '/passwort-zuruecksetzen' || pathname.startsWith('/passwort-zuruecksetzen/')) {
    return 'reset'
  }
  if (pathname === '/bestaetigen' || pathname.startsWith('/bestaetigen/')) {
    return 'verify'
  }
  if (pathname === '/organisation' || pathname.startsWith('/organisation/')) {
    return 'org'
  }
  if (pathname === '/verlauf' || pathname.startsWith('/verlauf/')) {
    return 'history'
  }
  return 'landing'
}

export function routeToPath(route: AppRoute): string {
  if (route === 'upload') {
    return '/upload'
  }
  if (route === 'legal') {
    return '/impressum'
  }
  if (route === 'help') {
    return '/hilfe'
  }
  if (route === 'login') {
    return '/anmelden'
  }
  if (route === 'register') {
    return '/registrieren'
  }
  if (route === 'forgot') {
    return '/passwort-vergessen'
  }
  if (route === 'reset') {
    return '/passwort-zuruecksetzen'
  }
  if (route === 'verify') {
    return '/bestaetigen'
  }
  if (route === 'org') {
    return '/organisation'
  }
  if (route === 'history') {
    return '/verlauf'
  }
  return '/'
}
