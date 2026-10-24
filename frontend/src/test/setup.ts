import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { CONSENT_STORAGE_KEY } from '../analytics'

afterEach((): void => {
  cleanup()
  localStorage.removeItem(CONSENT_STORAGE_KEY)
})

window.scrollTo = (): void => {
  return
}
