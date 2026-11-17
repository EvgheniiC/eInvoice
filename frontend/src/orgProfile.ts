export type OrgProfileFieldKey =
  | 'name'
  | 'taxNumber'
  | 'vatId'
  | 'iban'
  | 'accountantEmail'
  | 'invoiceContact'
  | 'invoicePhone'
  | 'invoiceEmail'
  | 'buyerEmail'
  | 'buyerReference'

export type OrgProfileFieldErrors = Partial<Record<OrgProfileFieldKey, string>>

const VAT_ID_RE: RegExp = /^[A-Z]{2}[A-Z0-9]{2,14}$/
const EMAIL_RE: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const PHONE_RE: RegExp = /^\+?[0-9][0-9 /\-()]{5,30}$/

export function compactAlnum(value: string): string {
  return value.replace(/[\s-]+/g, '').toUpperCase()
}

export function ibanChecksumOk(iban: string): boolean {
  if (iban.length < 15 || iban.length > 34) {
    return false
  }
  if (!/^[A-Z]{2}\d{2}[A-Z0-9]+$/.test(iban)) {
    return false
  }
  const rearranged: string = iban.slice(4) + iban.slice(0, 4)
  const numeric: string = rearranged.replace(/[A-Z]/g, (char: string): string =>
    String(char.charCodeAt(0) - 55),
  )
  let remainder: number = 0
  for (const digit of numeric) {
    remainder = (remainder * 10 + Number(digit)) % 97
  }
  return remainder === 1
}

export function validateOrgProfileFields(input: {
  name: string
  taxNumber: string
  vatId: string
  iban: string
  accountantEmail: string
  invoiceContact: string
  invoicePhone: string
  invoiceEmail: string
  buyerEmail: string
  buyerReference: string
}): OrgProfileFieldErrors {
  const errors: OrgProfileFieldErrors = {}
  const name: string = input.name.trim()
  if (name.length < 2) {
    errors.name = 'Bitte einen Namen mit mindestens 2 Zeichen angeben.'
  } else if (name.length > 120) {
    errors.name = 'Der Name darf höchstens 120 Zeichen haben.'
  }

  if (input.taxNumber.trim().length > 32) {
    errors.taxNumber = 'Steuernummer ist zu lang.'
  }

  const vatId: string = compactAlnum(input.vatId)
  if (vatId !== '' && !VAT_ID_RE.test(vatId)) {
    errors.vatId = 'USt-IdNr. ist ungültig. Beispiel: DE123456789'
  }

  const iban: string = compactAlnum(input.iban)
  if (iban !== '' && !ibanChecksumOk(iban)) {
    errors.iban = 'IBAN ist ungültig. Beispiel: DE89 3704 0044 0532 0130 00'
  }

  const email: string = input.accountantEmail.trim()
  if (email !== '' && !EMAIL_RE.test(email)) {
    errors.accountantEmail = 'E-Mail des Steuerberaters ist ungültig.'
  }

  if (input.invoiceContact.trim().length > 200) {
    errors.invoiceContact = 'Ansprechpartner ist zu lang.'
  }

  const phone: string = input.invoicePhone.trim()
  if (phone !== '' && !PHONE_RE.test(phone)) {
    errors.invoicePhone = 'Telefonnummer ist ungültig.'
  }

  const invoiceEmail: string = input.invoiceEmail.trim()
  if (invoiceEmail !== '' && !EMAIL_RE.test(invoiceEmail)) {
    errors.invoiceEmail = 'E-Mail des Verkäufers ist ungültig.'
  }

  const buyerEmail: string = input.buyerEmail.trim()
  if (buyerEmail !== '' && !EMAIL_RE.test(buyerEmail)) {
    errors.buyerEmail = 'E-Mail des Käufers ist ungültig.'
  }

  if (input.buyerReference.trim().length > 50) {
    errors.buyerReference = 'Käuferreferenz ist zu lang.'
  }

  return errors
}

export function orgProfileErrorsFromApi(message: string): OrgProfileFieldErrors {
  if (message.includes('USt-IdNr')) {
    return { vatId: message }
  }
  if (message.includes('IBAN')) {
    return { iban: message }
  }
  if (message.includes('Telefon')) {
    return { invoicePhone: message }
  }
  if (message.includes('Käufers')) {
    return { buyerEmail: message }
  }
  if (message.includes('Verkäufers')) {
    return { invoiceEmail: message }
  }
  if (message.includes('Käuferreferenz')) {
    return { buyerReference: message }
  }
  if (message.includes('Ansprechpartner')) {
    return { invoiceContact: message }
  }
  if (message.includes('Steuerberater') || message.includes('E-Mail')) {
    return { accountantEmail: message }
  }
  return {}
}

export function firstProfileErrorKey(errors: OrgProfileFieldErrors): OrgProfileFieldKey | null {
  const order: OrgProfileFieldKey[] = [
    'name',
    'taxNumber',
    'vatId',
    'iban',
    'accountantEmail',
    'invoiceContact',
    'invoicePhone',
    'invoiceEmail',
    'buyerEmail',
    'buyerReference',
  ]
  const found: OrgProfileFieldKey | undefined = order.find(
    (key: OrgProfileFieldKey): boolean => Boolean(errors[key]),
  )
  return found ?? null
}

export function profileFieldInputId(key: OrgProfileFieldKey): string {
  const ids: Record<OrgProfileFieldKey, string> = {
    name: 'org-name',
    taxNumber: 'org-tax-number',
    vatId: 'org-vat-id',
    iban: 'org-iban',
    accountantEmail: 'org-accountant-email',
    invoiceContact: 'org-invoice-contact',
    invoicePhone: 'org-invoice-phone',
    invoiceEmail: 'org-invoice-email',
    buyerEmail: 'org-buyer-email',
    buyerReference: 'org-buyer-reference',
  }
  return ids[key]
}
