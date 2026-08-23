export const SITE_ORIGIN: string = 'https://erechnung-smart.de'
export const SITE_NAME: string = 'eInvoice'

export type SeoRobots = 'index,follow' | 'noindex,nofollow'

export type SeoPage = {
  title: string
  description: string
  canonicalPath: string
  robots: SeoRobots
}

const DEFAULT_DESCRIPTION: string =
  'XRechnung und ZUGFeRD in Sekunden verstehen, prüfen und für die Buchhaltung exportieren.'

const LANDING: SeoPage = {
  title: 'XRechnung und ZUGFeRD prüfen | eInvoice',
  description: DEFAULT_DESCRIPTION,
  canonicalPath: '/',
  robots: 'index,follow',
}

function normalizePath(pathname: string): string {
  const trimmed: string = pathname.replace(/\/+$/, '')
  return trimmed === '' ? '/' : trimmed
}

export function seoForPath(pathname: string): SeoPage {
  const path: string = normalizePath(pathname)

  if (path === '/upload') {
    return {
      title: 'XRechnung oder ZUGFeRD hochladen | eInvoice',
      description:
        'XRechnung-XML oder ZUGFeRD-PDF hochladen, prüfen und als Excel, DATEV-CSV oder Steuerberater-Paket exportieren.',
      canonicalPath: '/upload',
      robots: 'index,follow',
    }
  }
  if (path === '/impressum') {
    return {
      title: 'Impressum | eInvoice',
      description: 'Impressum und Angaben zum Diensteanbieter von eInvoice.',
      canonicalPath: '/impressum',
      robots: 'index,follow',
    }
  }
  if (path === '/datenschutz') {
    return {
      title: 'Datenschutzerklärung | eInvoice',
      description:
        'Datenschutzerklärung: wie eInvoice hochgeladene Rechnungsdateien verarbeitet und wieder löscht.',
      canonicalPath: '/datenschutz',
      robots: 'index,follow',
    }
  }
  if (path === '/hilfe' || path === '/faq') {
    return {
      title: 'Hilfe und FAQ | eInvoice',
      description:
        'Antworten zu XRechnung, ZUGFeRD, Upload, Validierung und Export für die Buchhaltung.',
      canonicalPath: '/hilfe',
      robots: 'index,follow',
    }
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
