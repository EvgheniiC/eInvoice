import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import {
  completeBillingCheckout,
  createBillingCheckout,
  createBillingPortal,
  fetchBillingConfig,
  fetchMe,
} from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { PLAN_RANK, PUBLIC_PLANS, type PublicPlan, type PublicPlanCode } from '../content/plans'
import type { AppRoute } from '../routing'
import type {
  BillingCheckoutResponse,
  BillingCompleteResponse,
  BillingConfigResponse,
  BillingPortalResponse,
  MeResponse,
} from '../types/invoice'

type PricingPageProps = {
  onNavigate: (route: AppRoute, query?: string) => void
  session: MeResponse | null
  onSession: (session: MeResponse | null) => void
  locationSearch: string
  onLogout: () => void
}

export function PricingPage({
  onNavigate,
  session,
  onSession,
  locationSearch,
  onLogout,
}: PricingPageProps): JSX.Element {
  const [requestingPlan, setRequestingPlan] = useState<PublicPlanCode | null>(null)
  const [completing, setCompleting] = useState<boolean>(false)
  const [openingPortal, setOpeningPortal] = useState<boolean>(false)
  const [billingProvider, setBillingProvider] = useState<'stub' | 'stripe'>('stub')
  const [info, setInfo] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const completingRef: RefObject<string | null> = useRef<string | null>(null)
  const currentPlan: PublicPlanCode | null = toPublicPlanCode(session?.plan.code)
  const canManageSubscription: boolean =
    billingProvider === 'stripe' &&
    session?.role === 'inhaber' &&
    (currentPlan === 'plus' || currentPlan === 'team')

  useEffect(() => {
    let cancelled: boolean = false
    void fetchBillingConfig()
      .then((config: BillingConfigResponse) => {
        if (!cancelled) {
          setBillingProvider(config.provider)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setBillingProvider('stub')
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    const params: URLSearchParams = new URLSearchParams(
      locationSearch.startsWith('?') ? locationSearch.slice(1) : locationSearch,
    )
    const checkoutState: string | null = params.get('checkout')
    if (checkoutState === 'cancel') {
      setInfo('Zahlung abgebrochen. Der Tarif ist unverändert.')
      return
    }
    if (checkoutState !== 'success') {
      return
    }
    const sessionToken: string | null = params.get('session')
    if (sessionToken === null || sessionToken.length < 8) {
      setInfo('Zahlung eingegangen. Der Tarif wird aktiv, sobald Stripe die Zahlung bestätigt.')
      let cancelled: boolean = false
      const refresh = (): void => {
        void fetchMe().then((nextSession: MeResponse | null) => {
          if (!cancelled && nextSession !== null) {
            onSession(nextSession)
          }
        })
      }
      refresh()
      const timer: number = window.setTimeout(refresh, 2000)
      return () => {
        cancelled = true
        window.clearTimeout(timer)
      }
    }
    if (session === null) {
      onNavigate('login')
      return
    }
    if (completingRef.current === sessionToken) {
      return
    }
    completingRef.current = sessionToken
    setCompleting(true)
    setError(null)
    void completeBillingCheckout(sessionToken)
      .then(async (result: BillingCompleteResponse): Promise<void> => {
        const nextSession: MeResponse | null = await fetchMe()
        if (nextSession !== null) {
          onSession(nextSession)
        }
        setInfo(result.message)
        onNavigate('pricing')
      })
      .catch((err: unknown): void => {
        completingRef.current = null
        setError(err instanceof Error ? err.message : 'Zahlung konnte nicht bestätigt werden.')
      })
      .finally((): void => {
        setCompleting(false)
      })
  }, [locationSearch, session, onNavigate, onSession])

  async function startCheckout(planCode: PublicPlanCode): Promise<void> {
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
      const checkout: BillingCheckoutResponse = await createBillingCheckout(planCode)
      const url: URL = new URL(checkout.checkout_url, window.location.origin)
      if (url.hostname !== window.location.hostname) {
        window.location.assign(url.toString())
        return
      }
      onNavigate('pricing', url.search)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Zahlung konnte nicht gestartet werden.')
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
          Free prüft bis zu 10 Rechnungen pro Tag, eine Datei nach der anderen. Plus hebt das auf 100
          Prüfungen und 20 Dateien, Team auf 500 Prüfungen und 50 Dateien.
        </p>
      </header>

      <div className="pricing-grid">
        {PUBLIC_PLANS.map((plan: PublicPlan) => {
          const isCurrent: boolean = currentPlan === plan.code
          const canUpgrade: boolean =
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
              ) : showFreeCheck(plan.code, currentPlan) ? (
                <button type="button" className="btn btn--secondary" onClick={() => onNavigate('upload')}>
                  Kostenlos prüfen
                </button>
              ) : session === null ? (
                <button type="button" className="btn btn--primary" onClick={() => onNavigate('register')}>
                  Konto erstellen
                </button>
              ) : session.role !== 'inhaber' ? (
                <p className="page__limits">Nur der Inhaber kann den Tarif wechseln.</p>
              ) : canUpgrade ? (
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={requestingPlan !== null || completing}
                  onClick={() => {
                    void startCheckout(plan.code)
                  }}
                >
                  {requestingPlan === plan.code ? 'Weiterleitung…' : 'Jetzt upgraden'}
                </button>
              ) : null}
            </section>
          )
        })}
      </div>

      <p className="pricing-note">
        {billingProvider === 'stripe'
          ? 'Plus und Team sind Monatsabos über Stripe, zuzüglich gesetzlicher Umsatzsteuer. Der Tarif wird aktiv, sobald Stripe die Zahlung bestätigt. Karte, Rechnungen und Kündigung liegen im Kundenportal. Rechnungsdateien werden nur mit Ihrer ausdrücklichen Zustimmung gespeichert.'
          : 'Einführungspreise pro Monat zuzüglich gesetzlicher Umsatzsteuer. Die Zahlung ist noch eine Test-Rückkehr ohne echte Abbuchung: nach der Bestätigung wechselt der Tarif automatisch und das Limit von 10 Rechnungen entfällt. Rechnungsdateien werden nur mit Ihrer ausdrücklichen Zustimmung gespeichert.'}
      </p>
      {canManageSubscription ? (
        <p>
          <button
            type="button"
            className="btn btn--secondary"
            disabled={openingPortal}
            onClick={() => {
              setOpeningPortal(true)
              setError(null)
              void createBillingPortal()
                .then((portal: BillingPortalResponse) => {
                  window.location.assign(portal.portal_url)
                })
                .catch((err: unknown) => {
                  setError(err instanceof Error ? err.message : 'Kundenportal konnte nicht geöffnet werden.')
                  setOpeningPortal(false)
                })
            }}
          >
            {openingPortal ? 'Weiterleitung…' : 'Abo verwalten'}
          </button>
        </p>
      ) : null}
      {completing ? (
        <p className="status status--info" role="status">
          Zahlung wird bestätigt…
        </p>
      ) : null}
      {info ? (
        <p className="status status--info" role="status">
          {info}
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

function toPublicPlanCode(value: string | undefined): PublicPlanCode | null {
  if (value === 'free' || value === 'plus' || value === 'team') {
    return value
  }
  return null
}

function showFreeCheck(planCode: PublicPlanCode, currentPlan: PublicPlanCode | null): boolean {
  return planCode === 'free' && currentPlan !== 'plus' && currentPlan !== 'team'
}
