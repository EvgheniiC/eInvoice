export type AppRoute = 'landing' | 'upload' | 'legal'

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
  return 'landing'
}

export function routeToPath(route: AppRoute): string {
  if (route === 'upload') {
    return '/upload'
  }
  if (route === 'legal') {
    return '/impressum'
  }
  return '/'
}
