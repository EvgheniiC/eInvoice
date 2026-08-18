import { useEffect, useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { submitFeedback } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { FAQ_ITEMS, type FaqItem } from '../content/faq'
import type { AppRoute } from '../routing'
import type { FeedbackResponse } from '../types/invoice'

type HelpPageProps = {
  onNavigate: (route: AppRoute) => void
}

export function HelpPage({ onNavigate }: HelpPageProps): JSX.Element {
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

  return (
    <main id="main-content" className="page page--legal" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} />
        </div>
        <h1 tabIndex={-1}>Hilfe &amp; FAQ</h1>
        <p className="page__lead">
          Kurze Antworten zum Rechnungseingang — ohne Registrierung und ohne Rechnungsarchiv.
        </p>
      </header>

      {FAQ_ITEMS.map((item: FaqItem) => (
        <section key={item.id} id={item.id} className="legal-section">
          <h2>{item.question}</h2>
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
        </section>
      ))}

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
            Kein Datei-Upload. Maximal 2000 Zeichen. Support-Kontakt folgt mit den
            Betreiberangaben.
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

      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}
