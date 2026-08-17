import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { LEGAL_PAGES } from './content/legal'
import { LandingPage } from './pages/LandingPage'
import { LegalPage } from './pages/LegalPage'
import { UploadPage } from './pages/UploadPage'
import { pathToRoute, routeToPath, type AppRoute } from './routing'
import './App.css'

function App(): JSX.Element {
  const [route, setRoute] = useState<AppRoute>(() => pathToRoute(window.location.pathname))
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

  return (
    <>
      <a className="skip-link" href="#main-content">
        Zum Inhalt springen
      </a>
      {route === 'upload' ? (
        <UploadPage onNavigateHome={() => navigate('landing')} onNavigate={navigate} />
      ) : route === 'legal' ? (
        <LegalPage documents={LEGAL_PAGES} onNavigate={navigate} />
      ) : (
        <LandingPage onStart={() => navigate('upload')} onNavigate={navigate} />
      )}
    </>
  )
}

export default App
