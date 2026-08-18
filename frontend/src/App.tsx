import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { fetchMe, logoutAccount } from './api/client'
import { LEGAL_PAGES } from './content/legal'
import { HelpPage } from './pages/HelpPage'
import { LandingPage } from './pages/LandingPage'
import { LegalPage } from './pages/LegalPage'
import { LoginPage } from './pages/LoginPage'
import { OrgSettingsPage } from './pages/OrgSettingsPage'
import { RegisterPage } from './pages/RegisterPage'
import { UploadPage } from './pages/UploadPage'
import { VerifyPage } from './pages/VerifyPage'
import { pathToRoute, routeToPath, type AppRoute } from './routing'
import type { MeResponse } from './types/invoice'
import './App.css'

function App(): JSX.Element {
  const [route, setRoute] = useState<AppRoute>(() => pathToRoute(window.location.pathname))
  const [session, setSession] = useState<MeResponse | null>(null)
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
    if (isFirstRoute.current) {
      isFirstRoute.current = false
      return
    }
    const heading: HTMLElement | null = document.querySelector('#main-content h1')
    heading?.focus()
  }, [route])

  function navigate(next: AppRoute): void {
    const path: string = routeToPath(next)
    if (window.location.pathname !== path) {
      window.history.pushState(null, '', path)
    }
    window.scrollTo(0, 0)
    setRoute(next)
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
          onLoggedIn={setSession}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'register' ? (
        <RegisterPage
          onNavigate={navigate}
          session={session}
          onLogout={() => {
            void handleLogout()
          }}
        />
      ) : route === 'verify' ? (
        <VerifyPage
          onNavigate={navigate}
          onLoggedIn={setSession}
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
