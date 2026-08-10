export type AppRoute = 'landing' | 'upload'

export function pathToRoute(pathname: string): AppRoute {
  if (pathname === '/upload' || pathname.startsWith('/upload/')) {
    return 'upload'
  }
  return 'landing'
}

export function routeToPath(route: AppRoute): string {
  return route === 'upload' ? '/upload' : '/'
}
