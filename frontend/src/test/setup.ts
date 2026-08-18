import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'

afterEach((): void => {
  cleanup()
})

window.scrollTo = (): void => {
  return
}
