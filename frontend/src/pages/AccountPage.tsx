import { useState, type JSX } from 'react'
import { HistoryPanel } from '../components/HistoryPanel'
import { PageNav } from '../components/PageNav'
import { OrgSettingsPage } from './OrgSettingsPage'
import { SiteFooter } from '../components/SiteFooter'
import { REGISTRATION_BENEFITS, REGISTRATION_SUMMARY } from '../content/accountBenefits'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import type { MeResponse, PlanInfo } from '../types/invoice'

type AccountPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onSession: (session: MeResponse | null) => void
  onLogout: () => void
}

type AccountSection = 'overview' | 'history' | 'organization' | 'tariff'

type AccountAction = {
  href: string
  title: string
  text: string
  cta: string
}

const ACCOUNT_ACTIONS: readonly AccountAction[] = [
  {
    href: '/upload',
    title: 'Rechnung lesen',
    text: 'Eingangsrechnung öffnen: Betrag, Fälligkeit, IBAN und Export für den Steuerberater.',
    cta: 'Eingangsrechnung öffnen',
  },
  {
    href: '/erechnung-validation',
    title: 'Validieren',
    text: 'Prüfen, ob die Datei eine XRechnung oder ein ZUGFeRD/Factur-X ist.',
    cta: 'Validierung öffnen',
  },
  {
    href: '/erstellen',
    title: 'E-Rechnung erstellen',
    text: 'Aus einer normalen PDF einen Entwurf erzeugen. Eigene Angaben kommen aus dem Firmenprofil.',
    cta: 'E-Rechnung aus PDF',
  },
]

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

type AccountFact = {
  label: string
  value: string
}

function accountFacts(session: MeResponse): readonly AccountFact[] {
  const plan: PlanInfo = session.plan
  const facts: AccountFact[] = [
    { label: 'Organisation', value: session.organization_name },
    { label: 'E-Mail', value: session.email },
    { label: 'Rolle', value: roleLabel(session.role) },
    { label: 'Tarif', value: plan.name },
  ]
  if (!plan.quotas_enforced) {
    facts.push({ label: 'Kontingente', value: 'Noch nicht durchgesetzt.' })
    return facts
  }
  facts.push(
    {
      label: 'Prüfungen heute',
      value: `${String(plan.parse_used_today)}/${String(plan.parse_per_day)}`,
    },
    {
      label: 'Exporte heute',
      value: `${String(plan.export_used_today)}/${String(plan.export_per_day)}`,
    },
    {
      label: 'E-Rechnungen heute',
      value: `${String(plan.issue_used_today)}/${String(plan.issue_per_day)}`,
    },
  )
  return facts
}

function TariffSection({
  plan,
  onNavigate,
}: {
  plan: PlanInfo
  onNavigate: (route: AppRoute) => void
}): JSX.Element {
  const quotaText: string = plan.quotas_enforced
    ? `${String(plan.parse_used_today)}/${String(plan.parse_per_day)} Prüfungen, ` +
      `${String(plan.export_used_today)}/${String(plan.export_per_day)} Exporte, ` +
      `${String(plan.issue_used_today)}/${String(plan.issue_per_day)} E-Rechnungen.`
    : 'Kontingente sind noch nicht durchgesetzt.'

  return (
    <section className="account-tariff" aria-labelledby="account-tariff">
      <h2 id="account-tariff">Mein Tarif</h2>
      <p className="account-tariff__name">{plan.name}</p>
      <ul className="account-tariff__list">
        <li>Batch: {plan.allows_batch ? 'ja' : 'nein'}</li>
        <li>Historie: {plan.allows_history ? 'ja' : 'nein'}</li>
        <li>Dateien pro Auftrag: {plan.allows_batch ? String(plan.max_batch_files) : '1'}</li>
        <li>Max. Dateigröße: {String(plan.max_upload_size_mb)} MB</li>
        <li>Heute: {quotaText}</li>
      </ul>
      <p className="account-tariff__hint">{tariffHint(plan)}</p>
      <p className="account-tariff__ask">Möchten Sie den Tarif wechseln?</p>
      <button type="button" className="btn btn--secondary" onClick={() => onNavigate('pricing')}>
        Alle Tarife ansehen
      </button>
    </section>
  )
}

function BenefitList(): JSX.Element {
  return (
    <ul>
      {REGISTRATION_BENEFITS.map((benefit: string) => (
        <li key={benefit}>{benefit}</li>
      ))}
    </ul>
  )
}

function tariffHint(plan: PlanInfo): string {
  if (plan.code === 'free') {
    return 'Mit Plus stehen höhere Tageslimits, Batch und Historie zur Verfügung.'
  }
  if (plan.code === 'plus') {
    return 'Mit Team stehen höhere Kontingente zur Verfügung.'
  }
  return 'Rechnungsdateien werden ohne Zustimmung weiterhin nicht archiviert.'
}

export function AccountPage({
  onNavigate,
  session,
  onSession,
  onLogout,
}: AccountPageProps): JSX.Element {
  const [section, setSection] = useState<AccountSection>('overview')

  return (
    <main id="main-content" className="page page--account" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            Startseite
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>{session === null ? 'Konto' : `Hallo ${session.organization_name}`}</h1>
        {session === null ? <p className="page__lead">{REGISTRATION_SUMMARY}</p> : null}
      </header>

      {session === null ? (
        <>
          <section className="legal-section account-copy" aria-labelledby="account-benefits">
            <h2 id="account-benefits">Was die Registrierung bringt</h2>
            <BenefitList />
          </section>
          <div className="account-links">
            <button type="button" className="btn btn--primary" onClick={() => onNavigate('login')}>
              Anmelden
            </button>
            <button type="button" className="btn btn--secondary" onClick={() => onNavigate('register')}>
              Registrieren
            </button>
          </div>
        </>
      ) : (
        <div className="account-layout">
          <aside className="account-facts" aria-label="Kontodaten">
            <dl>
              {accountFacts(session).map((fact: AccountFact) => (
                <div key={fact.label}>
                  <dt>{fact.label}</dt>
                  <dd>{fact.value}</dd>
                </div>
              ))}
            </dl>
            <nav className="account-menu" aria-label="Kontobereiche">
              <button
                type="button"
                className="account-menu__item"
                aria-current={section === 'overview' ? 'page' : undefined}
                onClick={() => setSection('overview')}
              >
                Übersicht
              </button>
              <button
                type="button"
                className="account-menu__item"
                aria-current={section === 'history' ? 'page' : undefined}
                onClick={() => setSection('history')}
              >
                Verlauf
              </button>
              <button
                type="button"
                className="account-menu__item"
                aria-current={section === 'organization' ? 'page' : undefined}
                onClick={() => setSection('organization')}
              >
                Organisation Einstellungen
              </button>
              <button
                type="button"
                className="account-menu__item"
                aria-current={section === 'tariff' ? 'page' : undefined}
                onClick={() => setSection('tariff')}
              >
                Mein Tarif
              </button>
            </nav>
          </aside>
          <div className="account-main">
          {!session.email_verified ? (
            <p className="status status--info" role="status">
              Bitte bestätigen Sie die E-Mail-Adresse. Danach bleibt die Anmeldung auf diesem Konto.
            </p>
          ) : null}
          {section === 'history' ? (
            <section className="legal-section" aria-labelledby="account-history">
              <h2 id="account-history">Verlauf</h2>
              <HistoryPanel onNavigate={onNavigate} session={session} />
            </section>
          ) : null}
          {section === 'organization' ? (
            <section className="legal-section" aria-labelledby="account-organization">
              <h2 id="account-organization">Organisation Einstellungen</h2>
              <OrgSettingsPage
                embedded
                onNavigate={onNavigate}
                session={session}
                onSession={onSession}
                onLogout={onLogout}
              />
            </section>
          ) : null}
          {section === 'tariff' ? (
            <TariffSection plan={session.plan} onNavigate={onNavigate} />
          ) : null}
          {section === 'overview' ? (
            <>
              <section className="legal-section" aria-labelledby="account-actions">
                <h2 id="account-actions">Was Sie tun können</h2>
                <div className="account-grid">
                  {ACCOUNT_ACTIONS.map((action: AccountAction) => (
                    <article className="account-card" key={action.href}>
                      <h3>{action.title}</h3>
                      <p>{action.text}</p>
                      <AppLink href={action.href} className="btn btn--primary">
                        {action.cta}
                      </AppLink>
                    </article>
                  ))}
                </div>
              </section>
              <section className="legal-section account-copy" aria-labelledby="account-benefits">
                <h2 id="account-benefits">Was die Registrierung bringt</h2>
                <p className="page__limits">{REGISTRATION_SUMMARY}</p>
                <BenefitList />
              </section>
            </>
          ) : null}
          </div>
        </div>
      )}
      <SiteFooter />
    </main>
  )
}
