import { useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { requestPasswordReset } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { MeResponse, MessageResponse } from '../types/invoice'

type ForgotPasswordPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
  initialEmail: string
}

export function ForgotPasswordPage({
  onNavigate,
  session,
  onLogout,
  initialEmail,
}: ForgotPasswordPageProps): JSX.Element {
  const [email, setEmail] = useState<string>(initialEmail)
  const [sending, setSending] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (sending) {
      return
    }
    setSending(true)
    setError(null)
    setInfo(null)
    try {
      const result: MessageResponse = await requestPasswordReset(email)
      setInfo(result.message)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Zurücksetzen fehlgeschlagen.')
    } finally {
      setSending(false)
    }
  }

  return (
    <main id="main-content" className="page" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Passwort vergessen</h1>
        <p className="page__lead">
          Geben Sie die E-Mail-Adresse Ihres Kontos ein. Wenn ein bestätigtes Konto existiert,
          senden wir einen Link zum Festlegen eines neuen Passworts.
        </p>
      </header>

      <form className="auth-form" onSubmit={onSubmit}>
        <label htmlFor="forgot-email">E-Mail</label>
        <input
          id="forgot-email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          disabled={sending}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setEmail(event.target.value)}
        />
        <div className="auth-form__actions">
          <button type="submit" className="btn btn--primary" disabled={sending}>
            {sending ? 'Bitte warten…' : 'Link senden'}
          </button>
        </div>
      </form>
      {error ? (
        <p className="status status--error" role="alert">
          {error}
        </p>
      ) : null}
      {info ? (
        <p className="status status--info" role="status">
          {info}
        </p>
      ) : null}
      <p className="auth-form__switch">
        Zurück zur{' '}
        <button type="button" className="site-footer__link" onClick={() => onNavigate('login')}>
          Anmeldung
        </button>
      </p>
      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}
