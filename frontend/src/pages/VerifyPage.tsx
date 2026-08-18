import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { consumeMagicLink, verifyEmail } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { MeResponse } from '../types/invoice'

type VerifyPageProps = {
  onNavigate: (route: AppRoute) => void
  onLoggedIn: (session: MeResponse) => void
  session: MeResponse | null
  onLogout: () => void
}

export function VerifyPage({
  onNavigate,
  onLoggedIn,
  session,
  onLogout,
}: VerifyPageProps): JSX.Element {
  const [status, setStatus] = useState<string>('Link wird geprüft…')
  const [error, setError] = useState<string | null>(null)
  const onNavigateRef: RefObject<(route: AppRoute) => void> = useRef(onNavigate)
  const onLoggedInRef: RefObject<(session: MeResponse) => void> = useRef(onLoggedIn)
  onNavigateRef.current = onNavigate
  onLoggedInRef.current = onLoggedIn

  useEffect(() => {
    const params: URLSearchParams = new URLSearchParams(window.location.search)
    const token: string = params.get('token') ?? ''
    const kind: string = params.get('kind') ?? 'verify'
    if (token.trim() === '') {
      setError('Bestätigungslink unvollständig. Bitte den Link aus der E-Mail öffnen.')
      setStatus('')
      return
    }
    const run: () => Promise<void> = async (): Promise<void> => {
      try {
        const me: MeResponse =
          kind === 'magic' ? await consumeMagicLink(token) : await verifyEmail(token)
        onLoggedInRef.current(me)
        setStatus('Konto bestätigt. Sie werden zur Organisation weitergeleitet.')
        onNavigateRef.current('org')
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Bestätigung fehlgeschlagen.')
        setStatus('')
      }
    }
    void run()
  }, [])

  return (
    <main id="main-content" className="page" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>E-Mail bestätigen</h1>
        <p className="page__lead">Abschluss der Registrierung oder Anmeldung per Link.</p>
      </header>
      {status ? (
        <p className="status status--info" role="status">
          {status}
        </p>
      ) : null}
      {error ? (
        <p className="status status--error" role="alert">
          {error}
        </p>
      ) : null}
      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}
