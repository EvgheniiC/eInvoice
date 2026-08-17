import { useEffect, useState, type JSX } from 'react'
import { DATENSCHUTZ, IMPRESSUM } from './content/legal'
import { LandingPage } from './pages/LandingPage'
import { LegalPage } from './pages/LegalPage'
import { UploadPage } from './pages/UploadPage'
import { pathToRoute, routeToPath, type AppRoute } from './routing'
import './App.css'

function App(): JSX.Element {
  const [route, setRoute] = useState<AppRoute>(() => pathToRoute(window.location.pathname))

  useEffect(() => {
    function onPopState(): void {
      setRoute(pathToRoute(window.location.pathname))
    }
    window.addEventListener('popstate', onPopState)
    return () => {
      window.removeEventListener('popstate', onPopState)
    }
  }, [])

  function navigate(next: AppRoute): void {
    const path: string = routeToPath(next)
    if (window.location.pathname !== path) {
      window.history.pushState(null, '', path)
    }
    window.scrollTo(0, 0)
    setRoute(next)
  }

  if (route === 'upload') {
    return (
      <UploadPage onNavigateHome={() => navigate('landing')} onNavigate={navigate} />
    )
  }

  if (route === 'impressum') {
    return <LegalPage document={IMPRESSUM} onNavigate={navigate} />
  }

  if (route === 'datenschutz') {
    return <LegalPage document={DATENSCHUTZ} onNavigate={navigate} />
  }

  return <LandingPage onStart={() => navigate('upload')} onNavigate={navigate} />
}

export default App
