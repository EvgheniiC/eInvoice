import { useEffect, useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import {
  changeAccountPassword,
  fetchOrganization,
  updateOrganization,
} from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import {
  firstProfileErrorKey,
  orgProfileErrorsFromApi,
  profileFieldInputId,
  validateOrgProfileFields,
  type OrgProfileFieldErrors,
  type OrgProfileFieldKey,
} from '../orgProfile'
import type { AppRoute } from '../routing'
import type { MeResponse, MessageResponse, OrgResponse } from '../types/invoice'

type OrgSettingsPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onSession: (session: MeResponse | null) => void
  onLogout: () => void
}

function FieldError({ id, message }: { id: string; message?: string }): JSX.Element | null {
  if (!message) {
    return null
  }
  return (
    <p id={id} className="auth-form__field-error" role="alert">
      {message}
    </p>
  )
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
  const [taxNumber, setTaxNumber] = useState<string>('')
  const [vatId, setVatId] = useState<string>('')
  const [iban, setIban] = useState<string>('')
  const [accountantEmail, setAccountantEmail] = useState<string>('')
  const [invoiceContact, setInvoiceContact] = useState<string>('')
  const [invoicePhone, setInvoicePhone] = useState<string>('')
  const [invoiceEmail, setInvoiceEmail] = useState<string>('')
  const [buyerEmail, setBuyerEmail] = useState<string>('')
  const [buyerReference, setBuyerReference] = useState<string>('')
  const [historyEnabled, setHistoryEnabled] = useState<boolean>(session?.history_enabled ?? false)
  const [storeOriginals, setStoreOriginals] = useState<boolean>(
    session?.store_originals_enabled ?? false,
  )
  const [currentPassword, setCurrentPassword] = useState<string>('')
  const [newPassword, setNewPassword] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<OrgProfileFieldErrors>({})
  const [saving, setSaving] = useState<boolean>(false)
  const organizationId: string | null = session?.organization_id ?? null

  useEffect(() => {
    if (organizationId === null) {
      return
    }
    void fetchOrganization()
      .then((org: OrgResponse) => {
        setName(org.name)
        setTaxNumber(org.tax_number ?? '')
        setVatId(org.vat_id ?? '')
        setIban(org.iban ?? '')
        setAccountantEmail(org.accountant_email ?? '')
        setInvoiceContact(org.invoice_contact_name ?? '')
        setInvoicePhone(org.invoice_phone ?? '')
        setInvoiceEmail(org.invoice_email ?? '')
        setBuyerEmail(org.default_buyer_email ?? '')
        setBuyerReference(org.default_buyer_reference ?? '')
        setHistoryEnabled(org.history_enabled)
        setStoreOriginals(org.store_originals_enabled)
      })
      .catch(() => {
        // Keep session values if the extra GET fails.
      })
  }, [organizationId])

  if (session === null) {
    return (
      <main id="main-content" className="page" tabIndex={-1}>
        <header className="page__header">
          <div className="page__header-row">
            <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
              Startseite
            </button>
            <PageNav onNavigate={onNavigate} session={null} onLogout={onLogout} />
          </div>
          <h1 tabIndex={-1}>Organisation</h1>
          <p className="page__lead">Bitte zuerst anmelden.</p>
        </header>
        <button type="button" className="btn btn--primary" onClick={() => onNavigate('login')}>
          Anmelden
        </button>
        <SiteFooter />
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
    const nextErrors: OrgProfileFieldErrors = validateOrgProfileFields({
      name,
      taxNumber,
      vatId,
      iban,
      accountantEmail,
      invoiceContact,
      invoicePhone,
      invoiceEmail,
      buyerEmail,
      buyerReference,
    })
    if (Object.keys(nextErrors).length > 0) {
      setFieldErrors(nextErrors)
      setSaving(false)
      const firstKey: OrgProfileFieldKey | null = firstProfileErrorKey(nextErrors)
      if (firstKey !== null) {
        document.getElementById(profileFieldInputId(firstKey))?.focus()
      }
      return
    }
    setFieldErrors({})
    try {
      const updated: OrgResponse = await updateOrganization({
        name,
        tax_number: taxNumber,
        vat_id: vatId,
        iban,
        accountant_email: accountantEmail,
        invoice_contact_name: invoiceContact,
        invoice_phone: invoicePhone,
        invoice_email: invoiceEmail,
        default_buyer_email: buyerEmail,
        default_buyer_reference: buyerReference,
      })
      onSession({ ...session, organization_name: updated.name })
      setName(updated.name)
      setTaxNumber(updated.tax_number ?? '')
      setVatId(updated.vat_id ?? '')
      setIban(updated.iban ?? '')
      setAccountantEmail(updated.accountant_email ?? '')
      setInvoiceContact(updated.invoice_contact_name ?? '')
      setInvoicePhone(updated.invoice_phone ?? '')
      setInvoiceEmail(updated.invoice_email ?? '')
      setBuyerEmail(updated.default_buyer_email ?? '')
      setBuyerReference(updated.default_buyer_reference ?? '')
      setInfo('Firmenprofil gespeichert. Es erscheint im Steuerberater-Paket.')
    } catch (err: unknown) {
      const message: string =
        err instanceof Error ? err.message : 'Speichern fehlgeschlagen.'
      const mapped: OrgProfileFieldErrors = orgProfileErrorsFromApi(message)
      if (Object.keys(mapped).length > 0) {
        setFieldErrors(mapped)
        const firstKey: OrgProfileFieldKey | null = firstProfileErrorKey(mapped)
        if (firstKey !== null) {
          document.getElementById(profileFieldInputId(firstKey))?.focus()
        }
      } else {
        setError(message)
      }
    } finally {
      setSaving(false)
    }
  }

  function clearFieldError(key: OrgProfileFieldKey): void {
    setFieldErrors((current: OrgProfileFieldErrors): OrgProfileFieldErrors => {
      if (current[key] === undefined) {
        return current
      }
      const next: OrgProfileFieldErrors = { ...current }
      delete next[key]
      return next
    })
  }

  async function onSaveHistory(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (saving || session === null) {
      return
    }
    setSaving(true)
    setError(null)
    setInfo(null)
    try {
      const updated: OrgResponse = await updateOrganization({
        history_enabled: historyEnabled,
        store_originals_enabled: storeOriginals,
      })
      onSession({
        ...session,
        history_enabled: updated.history_enabled,
        store_originals_enabled: updated.store_originals_enabled,
      })
      setHistoryEnabled(updated.history_enabled)
      setStoreOriginals(updated.store_originals_enabled)
      setInfo(
        updated.history_enabled
          ? 'Verlauf gespeichert. Neue Prüfungen erscheinen unter Verlauf.'
          : 'Verlauf ausgeschaltet. Neue Prüfungen werden nicht mehr gespeichert.',
      )
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
  const issueUsed: string = `${String(session.plan.issue_used_today)}/${String(session.plan.issue_per_day)}`
  const quotaHint: string = session.plan.quotas_enforced
    ? `Heute: ${parseUsed} Prüfungen, ${exportUsed} Exporte, ${issueUsed} E-Rechnungen.`
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
            Startseite
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
          <li>
            Dateien pro Auftrag:{' '}
            {session.plan.allows_batch ? String(session.plan.max_batch_files) : '1'}
          </li>
          <li>Max. Dateigröße: {String(session.plan.max_upload_size_mb)} MB</li>
          <li>Parallele Prüfungen: {String(session.plan.max_parallel)}</li>
          <li>{quotaHint}</li>
        </ul>
        <p className="page__limits">{upgradeHint}</p>
        {session.plan.code !== 'team' ? (
          <button type="button" className="btn btn--secondary" onClick={() => onNavigate('pricing')}>
            Tarife vergleichen
          </button>
        ) : null}
      </section>

      {session.plan.allows_history ? (
        <form className="auth-form" onSubmit={onSaveHistory}>
          <h2>Verlauf</h2>
          <p className="auth-form__hint">
            Ohne Häkchen speichert eInvoice nach der Prüfung nichts. Gäste bleiben unverändert.
          </p>
          <label className="auth-form__check" htmlFor="history-enabled">
            <input
              id="history-enabled"
              type="checkbox"
              checked={historyEnabled}
              disabled={saving || session.role !== 'inhaber'}
              onChange={(event: ChangeEvent<HTMLInputElement>) => {
                const next: boolean = event.target.checked
                setHistoryEnabled(next)
                if (!next) {
                  setStoreOriginals(false)
                }
              }}
            />
            <span>
              Verlauf speichern
              <span className="auth-form__hint">
                Nur Metadaten und Datei-Hash: Datum, Lieferant, Nummer, Betrag, Status.
              </span>
            </span>
          </label>
          <label className="auth-form__check" htmlFor="store-originals">
            <input
              id="store-originals"
              type="checkbox"
              checked={storeOriginals}
              disabled={saving || session.role !== 'inhaber' || !historyEnabled}
              onChange={(event: ChangeEvent<HTMLInputElement>) => {
                const next: boolean = event.target.checked
                setStoreOriginals(next)
                if (next) {
                  setHistoryEnabled(true)
                }
              }}
            />
            <span>
              Dateien merken
              <span className="auth-form__hint">
                Originaldatei 30 Tage behalten, damit Sie das Steuerberater-Paket erneut laden
                können.
              </span>
            </span>
          </label>
          <button
            type="submit"
            className="btn btn--primary"
            disabled={saving || session.role !== 'inhaber'}
          >
            Zustimmung speichern
          </button>
        </form>
      ) : null}

      <form className="auth-form" noValidate onSubmit={onSaveOrg}>
        <h2>Firmenprofil</h2>
        <p className="auth-form__hint">
          Diese Angaben stehen im Steuerberater-ZIP unter mandant.txt. Später gelten sie
          auch für den Versand an die Kanzlei.
        </p>
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
          className={fieldErrors.name ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.name ? true : undefined}
          aria-describedby={fieldErrors.name ? 'org-name-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setName(event.target.value)
            clearFieldError('name')
          }}
        />
        <FieldError id="org-name-error" message={fieldErrors.name} />
        <label htmlFor="org-tax-number">
          Steuernummer <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-tax-number"
          name="tax_number"
          type="text"
          maxLength={32}
          autoComplete="off"
          value={taxNumber}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.taxNumber ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.taxNumber ? true : undefined}
          aria-describedby={fieldErrors.taxNumber ? 'org-tax-number-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setTaxNumber(event.target.value)
            clearFieldError('taxNumber')
          }}
        />
        <FieldError id="org-tax-number-error" message={fieldErrors.taxNumber} />
        <label htmlFor="org-vat-id">
          USt-IdNr. <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-vat-id"
          name="vat_id"
          type="text"
          maxLength={16}
          autoComplete="off"
          value={vatId}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.vatId ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.vatId ? true : undefined}
          aria-describedby={fieldErrors.vatId ? 'org-vat-id-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setVatId(event.target.value)
            clearFieldError('vatId')
          }}
        />
        <FieldError id="org-vat-id-error" message={fieldErrors.vatId} />
        <label htmlFor="org-iban">
          IBAN <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-iban"
          name="iban"
          type="text"
          maxLength={42}
          autoComplete="off"
          spellCheck={false}
          value={iban}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.iban ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.iban ? true : undefined}
          aria-describedby={fieldErrors.iban ? 'org-iban-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setIban(event.target.value)
            clearFieldError('iban')
          }}
        />
        <FieldError id="org-iban-error" message={fieldErrors.iban} />
        <label htmlFor="org-accountant-email">
          E-Mail Steuerberater <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-accountant-email"
          name="accountant_email"
          type="email"
          maxLength={254}
          autoComplete="off"
          value={accountantEmail}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.accountantEmail ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.accountantEmail ? true : undefined}
          aria-describedby={fieldErrors.accountantEmail ? 'org-accountant-email-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setAccountantEmail(event.target.value)
            clearFieldError('accountantEmail')
          }}
        />
        <FieldError id="org-accountant-email-error" message={fieldErrors.accountantEmail} />
        <h3>E-Rechnung</h3>
        <p className="auth-form__hint">
          Ansprechpartner, Telefon und E-Mail des Verkäufers füllen jeden Entwurf aus dem Profil.
          Käuferreferenz und E-Mail des Käufers gelten nur, wenn die PDF sie nicht enthält.
        </p>
        <label htmlFor="org-invoice-contact">
          Ansprechpartner <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-invoice-contact"
          name="invoice_contact_name"
          type="text"
          maxLength={200}
          autoComplete="name"
          value={invoiceContact}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.invoiceContact ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.invoiceContact ? true : undefined}
          aria-describedby={fieldErrors.invoiceContact ? 'org-invoice-contact-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setInvoiceContact(event.target.value)
            clearFieldError('invoiceContact')
          }}
        />
        <FieldError id="org-invoice-contact-error" message={fieldErrors.invoiceContact} />
        <label htmlFor="org-invoice-phone">
          Telefon <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-invoice-phone"
          name="invoice_phone"
          type="tel"
          maxLength={40}
          autoComplete="tel"
          value={invoicePhone}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.invoicePhone ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.invoicePhone ? true : undefined}
          aria-describedby={fieldErrors.invoicePhone ? 'org-invoice-phone-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setInvoicePhone(event.target.value)
            clearFieldError('invoicePhone')
          }}
        />
        <FieldError id="org-invoice-phone-error" message={fieldErrors.invoicePhone} />
        <label htmlFor="org-invoice-email">
          E-Mail des Verkäufers <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-invoice-email"
          name="invoice_email"
          type="email"
          maxLength={254}
          autoComplete="email"
          value={invoiceEmail}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.invoiceEmail ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.invoiceEmail ? true : undefined}
          aria-describedby={fieldErrors.invoiceEmail ? 'org-invoice-email-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setInvoiceEmail(event.target.value)
            clearFieldError('invoiceEmail')
          }}
        />
        <FieldError id="org-invoice-email-error" message={fieldErrors.invoiceEmail} />
        <label htmlFor="org-buyer-email">
          E-Mail des Käufers <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-buyer-email"
          name="default_buyer_email"
          type="email"
          maxLength={254}
          autoComplete="off"
          value={buyerEmail}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.buyerEmail ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.buyerEmail ? true : undefined}
          aria-describedby={fieldErrors.buyerEmail ? 'org-buyer-email-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setBuyerEmail(event.target.value)
            clearFieldError('buyerEmail')
          }}
        />
        <FieldError id="org-buyer-email-error" message={fieldErrors.buyerEmail} />
        <label htmlFor="org-buyer-reference">
          Käuferreferenz <span className="auth-form__optional">(Optional)</span>
        </label>
        <input
          id="org-buyer-reference"
          name="default_buyer_reference"
          type="text"
          maxLength={50}
          autoComplete="off"
          value={buyerReference}
          disabled={saving || session.role !== 'inhaber'}
          className={fieldErrors.buyerReference ? 'auth-form__input--error' : undefined}
          aria-invalid={fieldErrors.buyerReference ? true : undefined}
          aria-describedby={fieldErrors.buyerReference ? 'org-buyer-reference-error' : undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setBuyerReference(event.target.value)
            clearFieldError('buyerReference')
          }}
        />
        <FieldError id="org-buyer-reference-error" message={fieldErrors.buyerReference} />
        <button type="submit" className="btn btn--primary" disabled={saving || session.role !== 'inhaber'}>
          Profil speichern
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
      <SiteFooter />
    </main>
  )
}
