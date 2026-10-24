import { useEffect, useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { submitFeedback } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { SUPPORT_EMAIL } from '../content/contact'
import { FAQ_ITEMS, faqByPath, faqPageJsonLd, type FaqItem } from '../content/faq'
import { pagesByKind, type PublicPageLink } from '../content/publicPages'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import { SITE_ORIGIN } from '../seo'
import type { FeedbackResponse, MeResponse } from '../types/invoice'

type HelpPageProps = {
  pathname?: string
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

function FaqLinks({ item }: { item: FaqItem }): JSX.Element | null {
  if (!item.links || item.links.length === 0) {
    return null
  }
  return (
    <ul>
      {item.links.map((link: PublicPageLink) => (
        <li key={link.href}>
          <AppLink href={link.href}>{link.label}</AppLink>
        </li>
      ))}
    </ul>
  )
}

function FaqBody({ item }: { item: FaqItem }): JSX.Element {
  return (
    <>
      {item.paragraphs.map((paragraph: string, index: number) => (
        <p key={`${item.id}-p-${index}`}>{paragraph}</p>
      ))}
      {item.listItems ? (
        <ul>
          {item.listItems.map((entry: string, index: number) => (
            <li key={`${item.id}-li-${index}`}>{entry}</li>
          ))}
        </ul>
      ) : null}
      <FaqLinks item={item} />
    </>
  )
}

export function HelpPage({
  pathname = '/hilfe',
  onNavigate,
  session,
  onLogout,
}: HelpPageProps): JSX.Element {
  const [message, setMessage] = useState<string>('')
  const [contactEmail, setContactEmail] = useState<string>('')
  const [sending, setSending] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    const hash: string = window.location.hash.replace('#', '')
    if (!hash) {
      return
    }
    document.getElementById(hash)?.scrollIntoView({ block: 'start' })
  }, [])

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (sending) {
      return
    }
    setSending(true)
    setError(null)
    setSuccess(null)
    try {
      const result: FeedbackResponse = await submitFeedback({
        message,
        contact_email: contactEmail.trim() === '' ? null : contactEmail.trim(),
      })
      setSuccess(result.message)
      setMessage('')
      setContactEmail('')
    } catch (err: unknown) {
      const text: string =
        err instanceof Error ? err.message : 'Feedback konnte nicht gesendet werden.'
      setError(text)
    } finally {
      setSending(false)
    }
  }

  const article: FaqItem | null = faqByPath(pathname)
  const topics: readonly { path: string; h1: string }[] = pagesByKind('topic')

  return (
    <main id="main-content" className="page page--legal" tabIndex={-1}>
      {article === null ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: faqPageJsonLd(`${SITE_ORIGIN}/hilfe`) }}
        />
      ) : null}
      <header className="page__header">
        <div className="page__header-row">
          <AppLink href="/" className="page__home">
            ← eInvoice
          </AppLink>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>{article === null ? 'Hilfe & FAQ' : article.question}</h1>
        {article === null ? (
          <p className="page__lead">
            Kurze Antworten zum Rechnungseingang — ohne Registrierung und ohne Rechnungsarchiv.
          </p>
        ) : (
          <p className="page__lead">
            <AppLink href="/hilfe">Alle Fragen</AppLink>
          </p>
        )}
      </header>

      {article === null ? (
        <>
          <ul className="landing-benefits">
            {topics.map((topic: { path: string; h1: string }) => (
              <li key={topic.path}>
                <AppLink href={topic.path}>{topic.h1}</AppLink>
              </li>
            ))}
          </ul>
          {FAQ_ITEMS.map((item: FaqItem) => (
            <section key={item.id} id={item.id} className="legal-section">
              <h2>
                <AppLink href={item.path}>{item.question}</AppLink>
              </h2>
              <FaqBody item={item} />
            </section>
          ))}
        </>
      ) : (
        <section className="legal-section">
          <FaqBody item={article} />
        </section>
      )}

      <section id="feedback" className="legal-section">
        <h2>Feedback ohne Rechnungsdatei</h2>
        <p>
          Beschreiben Sie ein Problem mit der Website. Hängen Sie keine Rechnung an und fügen Sie
          keinen XML-, PDF- oder IBAN-Inhalt ein.
        </p>
        <form className="feedback-form" onSubmit={onSubmit}>
          <label htmlFor="feedback-message">Nachricht</label>
          <textarea
            id="feedback-message"
            name="message"
            required
            minLength={10}
            maxLength={2000}
            rows={6}
            value={message}
            disabled={sending}
            onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setMessage(event.target.value)}
          />
          <label htmlFor="feedback-email">E-Mail (optional, für Rückfragen)</label>
          <input
            id="feedback-email"
            name="contact_email"
            type="email"
            autoComplete="email"
            value={contactEmail}
            disabled={sending}
            onChange={(event: ChangeEvent<HTMLInputElement>) => setContactEmail(event.target.value)}
          />
          <p className="feedback-form__hint">
            Kein Datei-Upload. Maximal 2000 Zeichen. Support: {SUPPORT_EMAIL}
          </p>
          <button type="submit" className="btn btn--primary" disabled={sending}>
            {sending ? 'Wird gesendet…' : 'Nachricht senden'}
          </button>
        </form>
        {error ? (
          <p className="status status--error" role="alert">
            {error}
          </p>
        ) : null}
        {success ? (
          <p className="status status--info" role="status">
            {success}
          </p>
        ) : null}
      </section>

      <SiteFooter />
    </main>
  )
}
