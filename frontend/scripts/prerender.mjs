import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const distDir = path.join(root, 'dist')
const pagesPath = path.join(root, 'src', 'content', 'publicPages.json')
const origin = 'https://erechnung-smart.de'

/** @typedef {{ path: string, kind: string, h1: string, title: string, description: string, paragraphs: string[], listItems?: string[], links?: { href: string, label: string }[] }} Page */

const pages = /** @type {Page[]} */ (JSON.parse(fs.readFileSync(pagesPath, 'utf8')).pages)

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

function replaceOnce(html, pattern, replacement, label) {
  if (!pattern.test(html)) {
    throw new Error(`Prerender could not find ${label}`)
  }
  return html.replace(pattern, replacement)
}

function navHtml() {
  const links = [
    ['/upload', 'Rechnung hochladen'],
    ['/tarife', 'Tarife'],
    ['/hilfe', 'Hilfe'],
    ['/impressum', 'Impressum'],
    ['/datenschutz', 'Datenschutz'],
  ]
  const anchors = links
    .map(([href, label]) => `<a href="${href}">${escapeHtml(label)}</a>`)
    .join('')
  return `<nav aria-label="Seiten">${anchors}</nav>`
}

function paragraphHtml(page) {
  const paragraphs = page.paragraphs
    .map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`)
    .join('')
  const items = (page.listItems ?? [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join('')
  const list = items === '' ? '' : `<ul>${items}</ul>`
  const related = (page.links ?? [])
    .map((link) => `<li><a href="${link.href}">${escapeHtml(link.label)}</a></li>`)
    .join('')
  const relatedList = related === '' ? '' : `<ul>${related}</ul>`
  return `${paragraphs}${list}${relatedList}`
}

function extraHtml(page) {
  if (page.path === '/' || page.path === '/hilfe') {
    const topics = pages
      .filter((item) => item.kind === 'topic')
      .map((item) => `<li><a href="${item.path}">${escapeHtml(item.h1)}</a></li>`)
      .join('')
    return `<ul>${topics}</ul>`
  }
  if (page.kind === 'topic' || page.kind === 'faq') {
    return '<p><a href="/upload">Rechnung hochladen</a></p>'
  }
  return ''
}

function faqIndexHtml() {
  return pages
    .filter((item) => item.kind === 'faq')
    .map(
      (item) =>
        `<section><h2><a href="${item.path}">${escapeHtml(item.h1)}</a></h2>${paragraphHtml(item)}</section>`,
    )
    .join('')
}

function jsonLd(page) {
  if (page.path === '/hilfe') {
    return JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      url: `${origin}/hilfe`,
      mainEntity: pages
        .filter((item) => item.kind === 'faq')
        .map((item) => ({
          '@type': 'Question',
          name: item.h1,
          acceptedAnswer: {
            '@type': 'Answer',
            text: [...item.paragraphs, ...(item.listItems ?? [])].join(' '),
          },
        })),
    })
  }
  if (page.path === '/') {
    return JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'WebApplication',
      name: 'eInvoice',
      url: `${origin}/`,
      inLanguage: 'de',
      applicationCategory: 'BusinessApplication',
      operatingSystem: 'Web',
      description: page.description,
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'EUR' },
    })
  }
  return JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: page.h1,
    url: `${origin}${page.path === '/' ? '/' : page.path}`,
    inLanguage: 'de',
    description: page.description,
  })
}

function renderPage(template, page) {
  const canonical = `${origin}${page.path === '/' ? '/' : page.path}`
  let html = template
  html = replaceOnce(html, /<title>[^<]*<\/title>/, `<title>${escapeHtml(page.title)}</title>`, 'title')
  html = replaceOnce(
    html,
    /<meta[^>]*name="description"[^>]*>/,
    `<meta name="description" content="${escapeHtml(page.description)}" />`,
    'description',
  )
  html = replaceOnce(
    html,
    /<meta[^>]*property="og:title"[^>]*>/,
    `<meta property="og:title" content="${escapeHtml(page.title)}" />`,
    'og:title',
  )
  html = replaceOnce(
    html,
    /<meta[^>]*property="og:description"[^>]*>/,
    `<meta property="og:description" content="${escapeHtml(page.description)}" />`,
    'og:description',
  )
  html = replaceOnce(
    html,
    /<meta[^>]*property="og:url"[^>]*>/,
    `<meta property="og:url" content="${canonical}" />`,
    'og:url',
  )
  html = replaceOnce(
    html,
    /<link[^>]*rel="canonical"[^>]*>/,
    `<link rel="canonical" href="${canonical}" />`,
    'canonical',
  )
  html = replaceOnce(
    html,
    /<script type="application\/ld\+json">[\s\S]*?<\/script>/,
    `<script type="application/ld+json">${jsonLd(page)}</script>`,
    'json-ld',
  )
  const body = [
    '<div id="root">',
    '<main id="main-content">',
    navHtml(),
    `<h1>${escapeHtml(page.h1)}</h1>`,
    paragraphHtml(page),
    page.path === '/hilfe' ? faqIndexHtml() : '',
    extraHtml(page),
    '</main>',
    '</div>',
  ].join('')
  html = replaceOnce(html, /<div id="root">\s*<\/div>/, body, 'root')
  if (!html.includes(`<h1>${escapeHtml(page.h1)}</h1>`)) {
    throw new Error(`Prerender missed H1 for ${page.path}`)
  }
  return html
}

function writePage(template, page) {
  const html = renderPage(template, page)
  if (page.path === '/') {
    fs.writeFileSync(path.join(distDir, 'index.html'), html)
    return
  }
  const directory = path.join(distDir, page.path.slice(1))
  fs.mkdirSync(directory, { recursive: true })
  fs.writeFileSync(path.join(directory, 'index.html'), html)
}

function writeFaqRedirect() {
  const directory = path.join(distDir, 'faq')
  fs.mkdirSync(directory, { recursive: true })
  const html = `<!doctype html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="robots" content="noindex,follow" />
    <link rel="canonical" href="${origin}/hilfe" />
    <meta http-equiv="refresh" content="0; url=/hilfe" />
    <title>Hilfe und FAQ | eInvoice</title>
  </head>
  <body>
    <p><a href="/hilfe">Hilfe und FAQ</a></p>
  </body>
</html>
`
  fs.writeFileSync(path.join(directory, 'index.html'), html)
}

const template = fs.readFileSync(path.join(distDir, 'index.html'), 'utf8')
for (const page of pages) {
  writePage(template, page)
}
writeFaqRedirect()
console.log(`Prerendered ${pages.length} public pages`)
