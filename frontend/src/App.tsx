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
import { RegisterPage, type RegisterSuccess } from './pages/RegisterPage'
import { ResetPasswordPage } from './pages/ResetPasswordPage'
import { UploadPage } from './pages/UploadPage'
import { VerifyPage } from './pages/VerifyPage'
import { pathToRoute, routeToPath, type AppRoute } from './routing'
import { applySeo } from './seo'
import type { MeResponse } from './types/invoice'
import './App.css'

function App(): JSX.Element {
  const [route, setRoute] = useState<AppRoute>(() => pathToRoute(window.location.pathname))
  const [session, setSession] = useState<MeResponse | null>(null)
  const [loginNotice, setLoginNotice] = useState<string | null>(null)
  const [loginEmail, setLoginEmail] = useState<string>('')
  const [loginVerifyToken, setLoginVerifyToken] = useState<string | null>(null)
  const isFirstRoute: RefObject<boolean> = useRef<boolean>(true)

  useEffect(() => {
    function onPopState(): void {
      setRoute(pathToRoute(window.location.pathname))
    }
    window.addEventListener('popstate', onPopState)
    return () => {
      window.removeEventListener('popstate', onPopState)
    }
  }, [])

  useEffect(() => {
    void fetchMe().then((value: MeResponse | null) => {
      setSession(value)
    })
  }, [route])

  useEffect(() => {
    applySeo(window.location.pathname)
  }, [route])

  useEffect(() => {
    if (isFirstRoute.current) {
      isFirstRoute.current = false
      return
    }
    const heading: HTMLElement | null = document.querySelector('#main-content h1')
    heading?.focus()
  }, [route])

  function navigate(next: AppRoute, query: string = ''): void {
    const path: string = `${routeToPath(next)}${query}`
    const current: string = `${window.location.pathname}${window.location.search}`
    if (current !== path) {
      window.history.pushState(null, '', path)
    }
    window.scrollTo(0, 0)
    setRoute(next)
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
    <>
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
      ) : route === 'help' ? (
        <HelpPage
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
      ) : (
        <LandingPage
          onStart={() => navigate('upload')}
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      )}
    </>
  )
}

export default App
