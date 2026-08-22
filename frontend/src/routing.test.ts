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
    expect(pathToRoute('/anmelden')).toBe('login')
    expect(pathToRoute('/registrieren')).toBe('register')
    expect(pathToRoute('/passwort-vergessen')).toBe('forgot')
    expect(pathToRoute('/passwort-zuruecksetzen')).toBe('reset')
    expect(pathToRoute('/bestaetigen')).toBe('verify')
    expect(pathToRoute('/organisation')).toBe('org')
    expect(pathToRoute('/verlauf')).toBe('history')
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
    expect(routeToPath('login')).toBe('/anmelden')
    expect(routeToPath('register')).toBe('/registrieren')
    expect(routeToPath('forgot')).toBe('/passwort-vergessen')
    expect(routeToPath('reset')).toBe('/passwort-zuruecksetzen')
    expect(routeToPath('verify')).toBe('/bestaetigen')
    expect(routeToPath('org')).toBe('/organisation')
    expect(routeToPath('history')).toBe('/verlauf')
    expect(routeToPath('landing')).toBe('/')
  })
})
