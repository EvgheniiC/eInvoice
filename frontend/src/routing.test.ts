import { describe, expect, it } from 'vitest'
import { pathToRoute, routeToPath, type AppRoute } from './routing'

describe('pathToRoute', (): void => {
  it('maps the upload path', (): void => {
    const route: AppRoute = pathToRoute('/upload')
    expect(route).toBe('upload')
  })

  it('maps impressum, datenschutz and hilfe', (): void => {
    expect(pathToRoute('/impressum')).toBe('legal')
    expect(pathToRoute('/datenschutz')).toBe('legal')
    expect(pathToRoute('/impressum/')).toBe('legal')
    expect(pathToRoute('/hilfe')).toBe('help')
    expect(pathToRoute('/faq')).toBe('help')
  })

  it('maps unknown paths to landing', (): void => {
    expect(pathToRoute('/')).toBe('landing')
    expect(pathToRoute('/unknown')).toBe('landing')
  })
})

describe('routeToPath', (): void => {
  it('returns canonical paths', (): void => {
    expect(routeToPath('upload')).toBe('/upload')
    expect(routeToPath('legal')).toBe('/impressum')
    expect(routeToPath('help')).toBe('/hilfe')
    expect(routeToPath('landing')).toBe('/')
  })
})
