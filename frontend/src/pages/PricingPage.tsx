import { useState, type JSX } from 'react'
import { createPlanRequest } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { PLAN_RANK, PUBLIC_PLANS, type PublicPlan, type PublicPlanCode } from '../content/plans'
import type { AppRoute } from '../routing'
import type { MeResponse, PlanUpgradeRequestResponse } from '../types/invoice'

type PricingPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function PricingPage({
  onNavigate,
  session,
  onLogout,
}: PricingPageProps): JSX.Element {
  const [requestingPlan, setRequestingPlan] = useState<PublicPlanCode | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const currentPlan: PublicPlanCode | null = toPublicPlanCode(session?.plan.code)

  async function requestPlan(planCode: PublicPlanCode): Promise<void> {
    if (session === null) {
      onNavigate('register')
      return
    }
    if (session.role !== 'inhaber' || planCode === 'free') {
      return
    }
    setRequestingPlan(planCode)
    setInfo(null)
    setError(null)
    try {
      const request: PlanUpgradeRequestResponse = await createPlanRequest(planCode)
      setInfo(
        request.status === 'pending'
          ? `Ihre Anfrage für ${planName(planCode)} ist eingegangen. Wir melden uns per E-Mail.`
          : `Ihre Anfrage für ${planName(planCode)} wurde aktualisiert.`,
      )
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Tarifanfrage konnte nicht gesendet werden.')
    } finally {
      setRequestingPlan(null)
    }
  }

  return (
    <main id="main-content" className="page page--pricing" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Tarife</h1>
        <p className="page__lead">
          Einzelne Rechnungen bleiben kostenlos. Plus und Team ergänzen Batch, Verlauf und höhere
          Kontingente.
        </p>
      </header>

      <div className="pricing-grid">
        {PUBLIC_PLANS.map((plan: PublicPlan) => {
          const isCurrent: boolean = currentPlan === plan.code
          const canRequest: boolean =
            session !== null &&
            session.role === 'inhaber' &&
            currentPlan !== null &&
            PLAN_RANK[plan.code] > PLAN_RANK[currentPlan]
          return (
            <section
              key={plan.code}
              className={`pricing-card${plan.highlighted ? ' pricing-card--highlighted' : ''}`}
              aria-labelledby={`plan-${plan.code}`}
            >
              {plan.highlighted ? <p className="pricing-card__eyebrow">Empfohlen</p> : null}
              <h2 id={`plan-${plan.code}`}>{plan.name}</h2>
              <p className="pricing-card__price">
                {plan.priceMonthly}
                {plan.code !== 'free' ? <span> / Monat</span> : null}
              </p>
              <p>{plan.summary}</p>
              <ul>
                {plan.features.map((feature: string) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              {isCurrent ? (
                <p className="pricing-card__current">Aktueller Tarif</p>
              ) : plan.code === 'free' ? (
                <button type="button" className="btn btn--secondary" onClick={() => onNavigate('upload')}>
                  Kostenlos prüfen
                </button>
              ) : session === null ? (
                <button type="button" className="btn btn--primary" onClick={() => onNavigate('register')}>
                  Konto erstellen
                </button>
              ) : session.role !== 'inhaber' ? (
                <p className="page__limits">Nur der Inhaber kann einen Tarif anfragen.</p>
              ) : canRequest ? (
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={requestingPlan !== null}
                  onClick={() => {
                    void requestPlan(plan.code)
                  }}
                >
                  {requestingPlan === plan.code ? 'Anfrage wird gesendet…' : 'Freischaltung anfragen'}
                </button>
              ) : null}
            </section>
          )
        })}
      </div>

      <p className="pricing-note">
        Einführungspreise pro Monat zuzüglich gesetzlicher Umsatzsteuer. Plus und Team werden
        derzeit manuell freigeschaltet; es findet noch keine automatische Zahlung statt.
        Rechnungsdateien werden nur mit Ihrer ausdrücklichen Zustimmung gespeichert.
      </p>
      {info ? <p className="status status--info" role="status">{info}</p> : null}
      {error ? <p className="status status--error" role="alert">{error}</p> : null}
      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}

function toPublicPlanCode(value: string | undefined): PublicPlanCode | null {
  if (value === 'free' || value === 'plus' || value === 'team') {
    return value
  }
  return null
}

function planName(code: PublicPlanCode): string {
  return PUBLIC_PLANS.find((plan: PublicPlan): boolean => plan.code === code)?.name ?? code
}
