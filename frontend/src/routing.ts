export type AppRoute =
  | 'landing'
  | 'upload'
  | 'legal'
  | 'help'
  | 'login'
  | 'register'
  | 'verify'
  | 'org'

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
  if (pathname === '/bestaetigen' || pathname.startsWith('/bestaetigen/')) {
    return 'verify'
  }
  if (pathname === '/organisation' || pathname.startsWith('/organisation/')) {
    return 'org'
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
  if (route === 'verify') {
    return '/bestaetigen'
  }
  if (route === 'org') {
    return '/organisation'
  }
  return '/'
}
