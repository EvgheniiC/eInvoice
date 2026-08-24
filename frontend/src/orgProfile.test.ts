import { describe, expect, it } from 'vitest'
import {
  compactAlnum,
  ibanChecksumOk,
  orgProfileErrorsFromApi,
  validateOrgProfileFields,
  type OrgProfileFieldErrors,
} from './orgProfile'

describe('orgProfile validation', (): void => {
  it('accepts empty optional fields and a short name', (): void => {
    expect(
      validateOrgProfileFields({
        name: 'ABC',
        taxNumber: '',
        vatId: '',
        iban: '',
        accountantEmail: '',
      }),
    ).toEqual({})
  })

  it('flags placeholder USt-IdNr and IBAN together', (): void => {
    const errors: OrgProfileFieldErrors = validateOrgProfileFields({
      name: 'ABC',
      taxNumber: 'TEST12345',
      vatId: '123',
      iban: 'TEST12345',
      accountantEmail: '',
    })
    expect(errors.vatId).toMatch(/USt-IdNr/)
    expect(errors.iban).toMatch(/IBAN/)
    expect(errors.taxNumber).toBeUndefined()
  })

  it('accepts a checksum-valid German IBAN with spaces', (): void => {
    expect(compactAlnum('DE89 3704 0044 0532 0130 00')).toBe('DE89370400440532013000')
    expect(ibanChecksumOk('DE89370400440532013000')).toBe(true)
    expect(
      validateOrgProfileFields({
        name: 'ABC',
        taxNumber: '12/345/67890',
        vatId: 'DE123456789',
        iban: 'DE89 3704 0044 0532 0130 00',
        accountantEmail: 'sb@kanzlei.de',
      }),
    ).toEqual({})
  })

  it('maps API messages onto the matching field', (): void => {
    expect(orgProfileErrorsFromApi('USt-IdNr. ist ungültig.')).toEqual({
      vatId: 'USt-IdNr. ist ungültig.',
    })
    expect(orgProfileErrorsFromApi('IBAN ist ungültig.')).toEqual({ iban: 'IBAN ist ungültig.' })
  })
})
