import type { JSX } from 'react'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { REGISTRATION_BENEFITS, REGISTRATION_SUMMARY } from '../content/accountBenefits'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import type { MeResponse, PlanInfo } from '../types/invoice'

type AccountPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

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

function BenefitList(): JSX.Element {
  return (
    <ul>
      {REGISTRATION_BENEFITS.map((benefit: string) => (
        <li key={benefit}>{benefit}</li>
      ))}
    </ul>
  )
}

export function AccountPage({ onNavigate, session, onLogout }: AccountPageProps): JSX.Element {
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
          </aside>
          <div className="account-main">
          {!session.email_verified ? (
            <p className="status status--info" role="status">
              Bitte bestätigen Sie die E-Mail-Adresse. Danach bleibt die Anmeldung auf diesem Konto.
            </p>
          ) : null}
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
          <section className="legal-section" aria-labelledby="account-places">
            <h2 id="account-places">Einstellungen</h2>
            <div className="account-links">
              <button type="button" className="btn btn--secondary" onClick={() => onNavigate('org')}>
                Organisation
              </button>
              {session.plan.allows_history ? (
                <button
                  type="button"
                  className="btn btn--secondary"
                  onClick={() => onNavigate('history')}
                >
                  Verlauf
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn--secondary"
                  onClick={() => onNavigate('pricing')}
                >
                  Verlauf ab Plus
                </button>
              )}
              <button type="button" className="btn btn--secondary" onClick={() => onNavigate('pricing')}>
                Tarife
              </button>
              {session.is_admin ? (
                <button type="button" className="btn btn--secondary" onClick={() => onNavigate('stats')}>
                  Statistik
                </button>
              ) : null}
            </div>
          </section>
          </div>
        </div>
      )}
      <SiteFooter />
    </main>
  )
}
