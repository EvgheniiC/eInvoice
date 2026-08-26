import { describe, expect, it } from 'vitest'
import robotsTxt from '../public/robots.txt?raw'
import sitemapXml from '../public/sitemap.xml?raw'
import { applySeo, seoForPath, SITE_ORIGIN, type SeoPage } from './seo'

describe('seoForPath', (): void => {
  it('uses the homepage as canonical for unknown paths', (): void => {
    const page: SeoPage = seoForPath('/unknown')
    expect(page.canonicalPath).toBe('/')
    expect(page.robots).toBe('index,follow')
    expect(page.title).toContain('XRechnung')
  })

  it('indexes public product and legal pages', (): void => {
    expect(seoForPath('/upload').canonicalPath).toBe('/upload')
    expect(seoForPath('/tarife').canonicalPath).toBe('/tarife')
    expect(seoForPath('/impressum').title).toContain('Impressum')
    expect(seoForPath('/datenschutz').canonicalPath).toBe('/datenschutz')
    expect(seoForPath('/faq').canonicalPath).toBe('/hilfe')
    expect(seoForPath('/hilfe').robots).toBe('index,follow')
  })

  it('keeps account pages out of the index', (): void => {
    expect(seoForPath('/anmelden').robots).toBe('noindex,nofollow')
    expect(seoForPath('/registrieren').robots).toBe('noindex,nofollow')
    expect(seoForPath('/organisation').robots).toBe('noindex,nofollow')
    expect(seoForPath('/verlauf').robots).toBe('noindex,nofollow')
  })
})

describe('applySeo', (): void => {
  it('writes title, robots and canonical into the document head', (): void => {
    applySeo('/upload')

    expect(document.title).toBe('XRechnung oder ZUGFeRD hochladen | eInvoice')
    expect(document.querySelector('meta[name="robots"]')?.getAttribute('content')).toBe(
      'index,follow',
    )
    expect(document.querySelector('link[rel="canonical"]')?.getAttribute('href')).toBe(
      `${SITE_ORIGIN}/upload`,
    )
  })
})

describe('public crawl files', (): void => {
  it('publishes robots.txt with sitemap and API disallow', (): void => {
    expect(robotsTxt).toContain('User-agent: *')
    expect(robotsTxt).toContain('Disallow: /api/')
    expect(robotsTxt).toContain(`Sitemap: ${SITE_ORIGIN}/sitemap.xml`)
  })

  it('publishes sitemap.xml for the public pages', (): void => {
    expect(sitemapXml).toContain(`${SITE_ORIGIN}/</loc>`)
    expect(sitemapXml).toContain(`${SITE_ORIGIN}/upload</loc>`)
    expect(sitemapXml).toContain(`${SITE_ORIGIN}/tarife</loc>`)
    expect(sitemapXml).toContain(`${SITE_ORIGIN}/hilfe</loc>`)
    expect(sitemapXml).toContain(`${SITE_ORIGIN}/impressum</loc>`)
    expect(sitemapXml).toContain(`${SITE_ORIGIN}/datenschutz</loc>`)
    expect(sitemapXml).not.toContain('/anmelden')
  })
})
