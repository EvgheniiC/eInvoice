import raw from './publicPages.json'

export type PublicPageKind = 'home' | 'shell' | 'topic' | 'faq'

export type PublicPageLink = {
  href: string
  label: string
}

export type PublicPage = {
  path: string
  kind: PublicPageKind
  h1: string
  title: string
  description: string
  paragraphs: readonly string[]
  listItems?: readonly string[]
  links?: readonly PublicPageLink[]
}

function isKind(value: string): value is PublicPageKind {
  return value === 'home' || value === 'shell' || value === 'topic' || value === 'faq'
}

export const PUBLIC_PAGES: readonly PublicPage[] = raw.pages.map((page): PublicPage => {
  if (!isKind(page.kind)) {
    throw new Error(`Unknown public page kind: ${page.kind}`)
  }
  return {
    path: page.path,
    kind: page.kind,
    h1: page.h1,
    title: page.title,
    description: page.description,
    paragraphs: page.paragraphs,
    listItems: page.listItems,
    links: page.links,
  }
})

export function publicPageByPath(path: string): PublicPage | null {
  const normalized: string = path.replace(/\/+$/, '') || '/'
  return PUBLIC_PAGES.find((page: PublicPage): boolean => page.path === normalized) ?? null
}

export function pagesByKind(kind: PublicPageKind): readonly PublicPage[] {
  return PUBLIC_PAGES.filter((page: PublicPage): boolean => page.kind === kind)
}
