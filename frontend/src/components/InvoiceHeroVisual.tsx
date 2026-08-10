import type { JSX } from 'react'

/** Product visual: cryptic XML becomes a readable invoice. */
export function InvoiceHeroVisual(): JSX.Element {
  return (
    <div className="hero-visual" aria-hidden="true">
      <svg
        className="hero-visual__svg"
        viewBox="0 0 640 520"
        xmlns="http://www.w3.org/2000/svg"
        role="presentation"
      >
        <defs>
          <linearGradient id="paperGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#eef3f0" />
          </linearGradient>
          <linearGradient id="codeGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#24352c" />
            <stop offset="100%" stopColor="#1a2420" />
          </linearGradient>
          <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="18" stdDeviation="18" floodColor="#1a2420" floodOpacity="0.18" />
          </filter>
        </defs>

        <rect x="36" y="88" width="250" height="320" rx="10" fill="url(#codeGrad)" filter="url(#softShadow)" />
        <text x="56" y="122" fill="#7eb89a" fontFamily="ui-monospace, monospace" fontSize="13">
          {'<?xml version="1.0"?>'}
        </text>
        <text x="56" y="148" fill="#9ecfb5" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<Invoice>'}
        </text>
        <text x="68" y="172" fill="#c5d7cc" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<ID>RE-10482</ID>'}
        </text>
        <text x="68" y="196" fill="#c5d7cc" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<IssueDate>2026-03-12</IssueDate>'}
        </text>
        <text x="68" y="220" fill="#8aa396" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<AccountingSupplier…'}
        </text>
        <text x="68" y="244" fill="#8aa396" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<TaxTotal currencyID="EUR">'}
        </text>
        <text x="80" y="268" fill="#c5d7cc" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<TaxAmount>190.00</TaxAmount>'}
        </text>
        <text x="68" y="292" fill="#8aa396" fontFamily="ui-monospace, monospace" fontSize="12">
          {'</TaxTotal>'}
        </text>
        <text x="68" y="316" fill="#8aa396" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<LegalMonetaryTotal>'}
        </text>
        <text x="80" y="340" fill="#c5d7cc" fontFamily="ui-monospace, monospace" fontSize="12">
          {'<PayableAmount>1.190,00</PayableAmount>'}
        </text>
        <text x="56" y="372" fill="#9ecfb5" fontFamily="ui-monospace, monospace" fontSize="12">
          {'</Invoice>'}
        </text>

        <path
          className="hero-visual__arrow"
          d="M300 248 H348"
          stroke="#2f6b4f"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <path d="M340 236 L358 248 L340 260" fill="none" stroke="#2f6b4f" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

        <rect x="372" y="64" width="236" height="372" rx="12" fill="url(#paperGrad)" filter="url(#softShadow)" />
        <rect x="372" y="64" width="236" height="44" rx="12" fill="#2f6b4f" />
        <rect x="372" y="92" width="236" height="16" fill="#2f6b4f" />
        <text x="390" y="92" fill="#ffffff" fontFamily="Georgia, serif" fontSize="16" fontWeight="700">
          Rechnung
        </text>
        <text x="390" y="128" fill="#5c6770" fontFamily="sans-serif" fontSize="11">
          RE-10482 · 12.03.2026
        </text>
        <text x="390" y="158" fill="#1a1f24" fontFamily="sans-serif" fontSize="13" fontWeight="600">
          Muster GmbH
        </text>
        <text x="390" y="178" fill="#5c6770" fontFamily="sans-serif" fontSize="11">
          an Werkstatt Schmidt
        </text>
        <rect x="390" y="198" width="200" height="1" fill="#d5dcd7" />
        <text x="390" y="224" fill="#5c6770" fontFamily="sans-serif" fontSize="11">
          Positionen
        </text>
        <rect x="390" y="238" width="200" height="10" rx="3" fill="#dfe7e2" />
        <rect x="390" y="256" width="168" height="10" rx="3" fill="#e8eeea" />
        <rect x="390" y="274" width="186" height="10" rx="3" fill="#dfe7e2" />
        <rect x="390" y="304" width="200" height="1" fill="#d5dcd7" />
        <text x="390" y="332" fill="#5c6770" fontFamily="sans-serif" fontSize="11">
          Netto
        </text>
        <text x="530" y="332" fill="#1a1f24" fontFamily="sans-serif" fontSize="12" textAnchor="end">
          1.000,00 €
        </text>
        <text x="390" y="356" fill="#5c6770" fontFamily="sans-serif" fontSize="11">
          MwSt. 19%
        </text>
        <text x="530" y="356" fill="#1a1f24" fontFamily="sans-serif" fontSize="12" textAnchor="end">
          190,00 €
        </text>
        <text x="390" y="388" fill="#1a1f24" fontFamily="sans-serif" fontSize="14" fontWeight="700">
          Brutto
        </text>
        <text x="530" y="388" fill="#2f6b4f" fontFamily="sans-serif" fontSize="16" fontWeight="700" textAnchor="end">
          1.190,00 €
        </text>
        <rect x="390" y="408" width="88" height="22" rx="6" fill="#d9ebe1" />
        <text x="434" y="423" fill="#1f5a3d" fontFamily="sans-serif" fontSize="10" fontWeight="700" textAnchor="middle">
          OK
        </text>
      </svg>
    </div>
  )
}
