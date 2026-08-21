import { useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { resetAccountPassword } from '../api/client'
import { PageNav } from '../components/PageNav'
import { PasswordField } from '../components/PasswordField'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { MeResponse, MessageResponse } from '../types/invoice'

type ResetPasswordPageProps = {
  onNavigate: (route: AppRoute) => void
  onReset: (message: string) => void
  session: MeResponse | null
  onLogout: () => void
  token: string
}

const PASSWORD_MISMATCH: string = 'Die Passwörter stimmen nicht überein.'
const MISSING_TOKEN: string =
  'Der Link ist unvollständig. Bitte den Link aus der E-Mail öffnen.'

export function ResetPasswordPage({
  onNavigate,
  onReset,
  session,
  onLogout,
  token,
}: ResetPasswordPageProps): JSX.Element {
  const [password, setPassword] = useState<string>('')
  const [passwordConfirm, setPasswordConfirm] = useState<string>('')
  const [sending, setSending] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(token.trim() === '' ? MISSING_TOKEN : null)

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (sending) {
      return
    }
    if (token.trim() === '') {
      setError(MISSING_TOKEN)
      return
    }
    if (password !== passwordConfirm) {
      setError(PASSWORD_MISMATCH)
      return
    }
    setSending(true)
    setError(null)
    try {
      const result: MessageResponse = await resetAccountPassword(token, password)
      onReset(result.message)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Passwort konnte nicht gesetzt werden.')
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
        <h1 tabIndex={-1}>Neues Passwort setzen</h1>
        <p className="page__lead">
          Wählen Sie ein neues Passwort. Danach können Sie sich damit anmelden.
        </p>
      </header>

      <form className="auth-form" onSubmit={onSubmit}>
        <PasswordField
          id="reset-password"
          label="Neues Passwort (mind. 10 Zeichen)"
          name="password"
          autoComplete="new-password"
          value={password}
          disabled={sending || token.trim() === ''}
          minLength={10}
          maxLength={72}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setPassword(event.target.value)}
        />
        <PasswordField
          id="reset-password-confirm"
          label="Passwort wiederholen"
          name="password_confirm"
          autoComplete="new-password"
          value={passwordConfirm}
          disabled={sending || token.trim() === ''}
          minLength={10}
          maxLength={72}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setPasswordConfirm(event.target.value)}
        />
        <div className="auth-form__actions">
          <button type="submit" className="btn btn--primary" disabled={sending || token.trim() === ''}>
            {sending ? 'Bitte warten…' : 'Passwort speichern'}
          </button>
        </div>
      </form>
      {error ? (
        <p className="status status--error" role="alert">
          {error}
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
