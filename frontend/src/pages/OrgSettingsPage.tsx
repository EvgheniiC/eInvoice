import { useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { changeAccountPassword, updateOrganizationName } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { MeResponse, MessageResponse, OrgResponse } from '../types/invoice'

type OrgSettingsPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onSession: (session: MeResponse | null) => void
  onLogout: () => void
}

function roleLabel(role: string): string {
  if (role === 'inhaber') {
    return 'Inhaber'
  }
  if (role === 'buero') {
    return 'Büro'
  }
  if (role === 'export_only') {
    return 'Nur Export'
  }
  return role
}

export function OrgSettingsPage({
  onNavigate,
  session,
  onSession,
  onLogout,
}: OrgSettingsPageProps): JSX.Element {
  const [name, setName] = useState<string>(session?.organization_name ?? '')
  const [currentPassword, setCurrentPassword] = useState<string>('')
  const [newPassword, setNewPassword] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [saving, setSaving] = useState<boolean>(false)

  if (session === null) {
    return (
      <main id="main-content" className="page" tabIndex={-1}>
        <header className="page__header">
          <div className="page__header-row">
            <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
              ← eInvoice
            </button>
            <PageNav onNavigate={onNavigate} session={null} onLogout={onLogout} />
          </div>
          <h1 tabIndex={-1}>Organisation</h1>
          <p className="page__lead">Bitte zuerst anmelden.</p>
        </header>
        <button type="button" className="btn btn--primary" onClick={() => onNavigate('login')}>
          Anmelden
        </button>
        <SiteFooter onNavigate={onNavigate} />
      </main>
    )
  }

  async function onSaveOrg(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (saving || session === null) {
      return
    }
    setSaving(true)
    setError(null)
    setInfo(null)
    try {
      const updated: OrgResponse = await updateOrganizationName(name)
      onSession({ ...session, organization_name: updated.name })
      setInfo('Organisationsname gespeichert.')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Speichern fehlgeschlagen.')
    } finally {
      setSaving(false)
    }
  }

  async function onSavePassword(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (saving) {
      return
    }
    setSaving(true)
    setError(null)
    setInfo(null)
    try {
      const result: MessageResponse = await changeAccountPassword(currentPassword, newPassword)
      setInfo(result.message)
      setCurrentPassword('')
      setNewPassword('')
      onSession(null)
      onNavigate('login')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Passwortänderung fehlgeschlagen.')
    } finally {
      setSaving(false)
    }
  }

  const parseUsed: string = `${String(session.plan.parse_used_today)}/${String(session.plan.parse_per_day)}`
  const exportUsed: string = `${String(session.plan.export_used_today)}/${String(session.plan.export_per_day)}`
  const quotaHint: string = session.plan.quotas_enforced
    ? `Heute: ${parseUsed} Prüfungen, ${exportUsed} Exporte.`
    : 'Kontingente sind noch nicht durchgesetzt.'
  const upgradeHint: string =
    session.plan.code === 'free'
      ? 'Mit Plus stehen höhere Tageslimits, Batch und Historie zur Verfügung.'
      : session.plan.code === 'plus'
        ? 'Mit Team stehen höhere Kontingente zur Verfügung.'
        : 'Rechnungsdateien werden ohne Zustimmung weiterhin nicht archiviert.'

  return (
    <main id="main-content" className="page" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Organisation</h1>
        <p className="page__lead">
          {session.email} · {roleLabel(session.role)} · Tarif {session.plan.name}
        </p>
      </header>

      <section className="legal-section">
        <h2>Tarif</h2>
        <ul>
          <li>Code: {session.plan.code}</li>
          <li>Batch: {session.plan.allows_batch ? 'ja' : 'nein'}</li>
          <li>Historie: {session.plan.allows_history ? 'ja' : 'nein'}</li>
          <li>Max. Dateigröße: {String(session.plan.max_upload_size_mb)} MB</li>
          <li>Parallele Prüfungen: {String(session.plan.max_parallel)}</li>
          <li>{quotaHint}</li>
        </ul>
        <p className="page__limits">{upgradeHint}</p>
      </section>

      <form className="auth-form" onSubmit={onSaveOrg}>
        <label htmlFor="org-name">Name der Organisation</label>
        <input
          id="org-name"
          name="organization"
          type="text"
          required
          minLength={2}
          maxLength={120}
          value={name}
          disabled={saving || session.role !== 'inhaber'}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setName(event.target.value)}
        />
        <button type="submit" className="btn btn--primary" disabled={saving || session.role !== 'inhaber'}>
          Name speichern
        </button>
      </form>

      <form className="auth-form" onSubmit={onSavePassword}>
        <label htmlFor="pw-current">Aktuelles Passwort</label>
        <input
          id="pw-current"
          type="password"
          autoComplete="current-password"
          required
          value={currentPassword}
          disabled={saving}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setCurrentPassword(event.target.value)}
        />
        <label htmlFor="pw-new">Neues Passwort</label>
        <input
          id="pw-new"
          type="password"
          autoComplete="new-password"
          required
          minLength={10}
          maxLength={72}
          value={newPassword}
          disabled={saving}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setNewPassword(event.target.value)}
        />
        <button type="submit" className="btn btn--primary" disabled={saving}>
          Passwort ändern
        </button>
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
      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}
