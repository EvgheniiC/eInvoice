import { useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { loginAccount, requestMagicLink } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { MeResponse, MessageResponse } from '../types/invoice'

type LoginPageProps = {
  onNavigate: (route: AppRoute) => void
  onLoggedIn: (session: MeResponse) => void
  session: MeResponse | null
  onLogout: () => void
}

export function LoginPage({
  onNavigate,
  onLoggedIn,
  session,
  onLogout,
}: LoginPageProps): JSX.Element {
  const [email, setEmail] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [sending, setSending] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [magicInfo, setMagicInfo] = useState<string | null>(null)

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (sending) {
      return
    }
    setSending(true)
    setError(null)
    setMagicInfo(null)
    try {
      const me: MeResponse = await loginAccount(email, password)
      onLoggedIn(me)
      onNavigate('org')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Anmeldung fehlgeschlagen.')
    } finally {
      setSending(false)
    }
  }

  async function onMagicLink(): Promise<void> {
    if (sending || email.trim() === '') {
      setError('Bitte zuerst die E-Mail-Adresse eintragen.')
      return
    }
    setSending(true)
    setError(null)
    try {
      const result: MessageResponse = await requestMagicLink(email)
      setMagicInfo(result.message)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Anmeldelink fehlgeschlagen.')
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
        <h1 tabIndex={-1}>Anmelden</h1>
        <p className="page__lead">
          Für Verlauf und Sammel-Export (später). Eine einzelne Rechnung können Sie weiter ohne
          Konto prüfen.
        </p>
      </header>

      <form className="auth-form" onSubmit={onSubmit}>
        <label htmlFor="login-email">E-Mail</label>
        <input
          id="login-email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          disabled={sending}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setEmail(event.target.value)}
        />
        <label htmlFor="login-password">Passwort</label>
        <input
          id="login-password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          minLength={1}
          value={password}
          disabled={sending}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setPassword(event.target.value)}
        />
        <div className="auth-form__actions">
          <button type="submit" className="btn btn--primary" disabled={sending}>
            {sending ? 'Bitte warten…' : 'Mit Passwort anmelden'}
          </button>
          <button type="button" className="btn btn--secondary" disabled={sending} onClick={onMagicLink}>
            Anmeldelink per E-Mail
          </button>
        </div>
      </form>
      {error ? (
        <p className="status status--error" role="alert">
          {error}
        </p>
      ) : null}
      {magicInfo ? (
        <p className="status status--info" role="status">
          {magicInfo}
        </p>
      ) : null}
      <p className="auth-form__switch">
        Noch kein Konto?{' '}
        <button type="button" className="site-footer__link" onClick={() => onNavigate('register')}>
          Registrieren
        </button>
      </p>
      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}
