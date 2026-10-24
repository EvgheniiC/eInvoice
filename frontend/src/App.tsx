import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { fetchMe, logoutAccount } from './api/client'
import { LEGAL_PAGES } from './content/legal'
import { HelpPage } from './pages/HelpPage'
import { ForgotPasswordPage } from './pages/ForgotPasswordPage'
import { LandingPage } from './pages/LandingPage'
import { LegalPage } from './pages/LegalPage'
import { LoginPage } from './pages/LoginPage'
import { HistoryPage } from './pages/HistoryPage'
import { OrgSettingsPage } from './pages/OrgSettingsPage'
import { PricingPage } from './pages/PricingPage'
import { AdminStatsPage } from './pages/AdminStatsPage'
import { RegisterPage, type RegisterSuccess } from './pages/RegisterPage'
import { ResetPasswordPage } from './pages/ResetPasswordPage'
import { TopicPage } from './pages/TopicPage'
import { UploadPage } from './pages/UploadPage'
import { FollowPathProvider } from './navigation'
import { VerifyPage } from './pages/VerifyPage'
import { pathToRoute, routeToPath, type AppRoute } from './routing'
import { applySeo } from './seo'
import type { MeResponse } from './types/invoice'
import './App.css'

function App(): JSX.Element {
  const [route, setRoute] = useState<AppRoute>(() => pathToRoute(window.location.pathname))
  const [pathname, setPathname] = useState<string>(() => window.location.pathname)
  const [locationSearch, setLocationSearch] = useState<string>(() => window.location.search)
  const [session, setSession] = useState<MeResponse | null>(null)
  const [sessionReady, setSessionReady] = useState<boolean>(false)
  const [loginNotice, setLoginNotice] = useState<string | null>(null)
  const [loginEmail, setLoginEmail] = useState<string>('')
  const [loginVerifyToken, setLoginVerifyToken] = useState<string | null>(null)
  const isFirstRoute: RefObject<boolean> = useRef<boolean>(true)

  useEffect(() => {
    function onPopState(): void {
      setPathname(window.location.pathname)
      setRoute(pathToRoute(window.location.pathname))
      setLocationSearch(window.location.search)
    }
    window.addEventListener('popstate', onPopState)
    return () => {
      window.removeEventListener('popstate', onPopState)
    }
  }, [])

  useEffect(() => {
    let cancelled: boolean = false
    setSessionReady(false)
    void fetchMe().then((value: MeResponse | null) => {
      if (cancelled) {
        return
      }
      setSession(value)
      setSessionReady(true)
    })
    return () => {
      cancelled = true
    }
  }, [route])

  useEffect(() => {
    applySeo(window.location.pathname)
  }, [route, pathname])

  useEffect(() => {
    const normalized: string = window.location.pathname.replace(/\/+$/, '') || '/'
    if (normalized !== '/faq') {
      return
    }
    window.history.replaceState(null, '', '/hilfe')
    setPathname('/hilfe')
    setRoute('help')
  }, [])

  useEffect(() => {
    if (isFirstRoute.current) {
      isFirstRoute.current = false
      return
    }
    const heading: HTMLElement | null = document.querySelector('#main-content h1')
    heading?.focus()
  }, [route])

  function navigate(next: AppRoute, query: string = ''): void {
    const normalizedQuery: string =
      query === '' ? '' : query.startsWith('?') ? query : `?${query}`
    const path: string = `${routeToPath(next)}${normalizedQuery}`
    const current: string = `${window.location.pathname}${window.location.search}`
    if (current !== path) {
      window.history.pushState(null, '', path)
    }
    window.scrollTo(0, 0)
    setPathname(routeToPath(next))
    setLocationSearch(normalizedQuery)
    setRoute(next)
  }

  function followPath(path: string): void {
    const current: string = `${window.location.pathname}${window.location.search}`
    if (current !== path) {
      window.history.pushState(null, '', path)
    }
    window.scrollTo(0, 0)
    setPathname(path)
    setLocationSearch('')
    setRoute(pathToRoute(path))
  }

  function handleRegistered(result: RegisterSuccess): void {
    setLoginNotice(result.message)
    setLoginEmail(result.email)
    setLoginVerifyToken(result.verificationToken)
    navigate('login')
  }

  function handleLoggedIn(value: MeResponse): void {
    setLoginNotice(null)
    setLoginVerifyToken(null)
    setSession(value)
  }

  function handlePasswordReset(message: string): void {
    setLoginNotice(message)
    setLoginVerifyToken(null)
    setSession(null)
    navigate('login')
  }

  function handleForgotPassword(email: string): void {
    setLoginEmail(email.trim())
    navigate('forgot')
  }

  async function handleLogout(): Promise<void> {
    await logoutAccount()
    setSession(null)
    navigate('landing')
  }

  return (
    <FollowPathProvider followPath={followPath}>
      <a className="skip-link" href="#main-content">
        Zum Inhalt springen
      </a>
      {route === 'upload' ? (
        <UploadPage
          onNavigateHome={() => navigate('landing')}
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'legal' ? (
        <LegalPage
          documents={LEGAL_PAGES}
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'topic' ? (
        <TopicPage
          pathname={pathname}
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'help' ? (
        <HelpPage
          pathname={pathname}
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'login' ? (
        <LoginPage
          onNavigate={navigate}
          onLoggedIn={handleLoggedIn}
          onForgotPassword={handleForgotPassword}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
          notice={loginNotice}
          initialEmail={loginEmail}
          verificationToken={loginVerifyToken}
        />
      ) : route === 'register' ? (
        <RegisterPage
          onNavigate={navigate}
          onRegistered={handleRegistered}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'forgot' ? (
        <ForgotPasswordPage
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
          initialEmail={loginEmail}
        />
      ) : route === 'reset' ? (
        <ResetPasswordPage
          onNavigate={navigate}
          onReset={handlePasswordReset}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
          token={new URLSearchParams(window.location.search).get('token') ?? ''}
        />
      ) : route === 'verify' ? (
        <VerifyPage
          onNavigate={navigate}
          onLoggedIn={handleLoggedIn}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'org' ? (
        <OrgSettingsPage
          onNavigate={navigate}
          session={session}
          onSession={setSession}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'history' ? (
        <HistoryPage
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'stats' ? (
        <AdminStatsPage
          onNavigate={navigate}
          session={session}
          sessionReady={sessionReady}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'pricing' ? (
        <PricingPage
          onNavigate={navigate}
          session={session}
          onSession={setSession}
          locationSearch={locationSearch}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : (
        <LandingPage
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      )}
    </FollowPathProvider>
  )
}

export default App
