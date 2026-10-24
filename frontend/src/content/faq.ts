import { pagesByKind, type PublicPage, type PublicPageLink } from './publicPages'

export type FaqItem = {
  id: string
  path: string
  question: string
  paragraphs: readonly string[]
  listItems?: readonly string[]
  links?: readonly PublicPageLink[]
}

function faqId(path: string): string {
  const id: string = path.slice('/hilfe/'.length)
  if (id === '' || id.includes('/')) {
    throw new Error(`FAQ path must be /hilfe/<id>: ${path}`)
  }
  return id
}

export const FAQ_ITEMS: readonly FaqItem[] = pagesByKind('faq').map(
  (page: PublicPage): FaqItem => ({
    id: faqId(page.path),
    path: page.path,
    question: page.h1,
    paragraphs: page.paragraphs,
    listItems: page.listItems,
    links: page.links,
  }),
)

export function faqByPath(pathname: string): FaqItem | null {
  const normalized: string = pathname.replace(/\/+$/, '') || '/'
  return FAQ_ITEMS.find((item: FaqItem): boolean => item.path === normalized) ?? null
}

export function faqPageJsonLd(pageUrl: string): string {
  return JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    url: pageUrl,
    mainEntity: FAQ_ITEMS.map((item: FaqItem) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: [...item.paragraphs, ...(item.listItems ?? [])].join(' '),
      },
    })),
  })
}
