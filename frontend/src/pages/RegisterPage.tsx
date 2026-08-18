import { useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { registerAccount } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { MeResponse, RegisterResponse } from '../types/invoice'

type RegisterPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function RegisterPage({ onNavigate, session, onLogout }: RegisterPageProps): JSX.Element {
  const [email, setEmail] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [organizationName, setOrganizationName] = useState<string>('')
  const [sending, setSending] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (sending) {
      return
    }
    setSending(true)
    setError(null)
    setSuccess(null)
    try {
      const result: RegisterResponse = await registerAccount(email, password, organizationName)
      setSuccess(result.message)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registrierung fehlgeschlagen.')
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
        <h1 tabIndex={-1}>Konto erstellen</h1>
        <p className="page__lead">
          E-Mail, Passwort und Name der Organisation. Rechnungen werden weiterhin nicht gespeichert,
          solange Sie das nicht später ausdrücklich erlauben.
        </p>
      </header>

      <form className="auth-form" onSubmit={onSubmit}>
        <label htmlFor="register-org">Organisation</label>
        <input
          id="register-org"
          name="organization"
          type="text"
          autoComplete="organization"
          required
          minLength={2}
          maxLength={120}
          value={organizationName}
          disabled={sending}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setOrganizationName(event.target.value)}
        />
        <label htmlFor="register-email">E-Mail</label>
        <input
          id="register-email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          disabled={sending}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setEmail(event.target.value)}
        />
        <label htmlFor="register-password">Passwort (mind. 10 Zeichen)</label>
        <input
          id="register-password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={10}
          maxLength={72}
          value={password}
          disabled={sending}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setPassword(event.target.value)}
        />
        <button type="submit" className="btn btn--primary" disabled={sending}>
          {sending ? 'Bitte warten…' : 'Registrieren'}
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
      <p className="auth-form__switch">
        Bereits registriert?{' '}
        <button type="button" className="site-footer__link" onClick={() => onNavigate('login')}>
          Anmelden
        </button>
      </p>
      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}
