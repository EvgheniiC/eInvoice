export type AppRoute = 'landing' | 'upload' | 'impressum' | 'datenschutz'

export function pathToRoute(pathname: string): AppRoute {
  if (pathname === '/upload' || pathname.startsWith('/upload/')) {
    return 'upload'
  }
  if (pathname === '/impressum' || pathname.startsWith('/impressum/')) {
    return 'impressum'
  }
  if (pathname === '/datenschutz' || pathname.startsWith('/datenschutz/')) {
    return 'datenschutz'
  }
  return 'landing'
}

export function routeToPath(route: AppRoute): string {
  if (route === 'upload') {
    return '/upload'
  }
  if (route === 'impressum') {
    return '/impressum'
  }
  if (route === 'datenschutz') {
    return '/datenschutz'
  }
  return '/'
}
