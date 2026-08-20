import { useState, type ChangeEvent, type JSX } from 'react'

type PasswordFieldProps = {
  id: string
  label: string
  name: string
  autoComplete: string
  value: string
  disabled: boolean
  required?: boolean
  minLength?: number
  maxLength?: number
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
}

type MonkeyIconProps = {
  eyesOpen: boolean
}

function MonkeyIcon({ eyesOpen }: MonkeyIconProps): JSX.Element {
  return (
    <svg className="password-monkey" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <circle cx="12" cy="22" r="10" fill="#7a6243" />
      <circle cx="52" cy="22" r="10" fill="#7a6243" />
      <circle cx="12" cy="22" r="5.5" fill="#e4c9a3" />
      <circle cx="52" cy="22" r="5.5" fill="#e4c9a3" />
      <circle cx="32" cy="34" r="22" fill="#8d7048" />
      <ellipse cx="32" cy="39" rx="15" ry="13" fill="#edd9bd" />
      <g className={eyesOpen ? 'password-monkey__eyes password-monkey__eyes--open' : 'password-monkey__eyes'}>
        <ellipse cx="24" cy="34" rx="4.2" ry="5.2" fill="#1a1f24" />
        <ellipse cx="40" cy="34" rx="4.2" ry="5.2" fill="#1a1f24" />
        <circle cx="25.4" cy="32.4" r="1.35" fill="#ffffff" />
        <circle cx="41.4" cy="32.4" r="1.35" fill="#ffffff" />
      </g>
      <ellipse cx="32" cy="42" rx="2.6" ry="1.7" fill="#6b4a2b" />
      <path
        d="M26 47.5 Q32 52 38 47.5"
        fill="none"
        stroke="#6b4a2b"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <g className={eyesOpen ? 'password-monkey__hands password-monkey__hands--open' : 'password-monkey__hands'}>
        <ellipse className="password-monkey__hand password-monkey__hand--left" cx="21" cy="33" rx="10" ry="7.5" fill="#8d7048" />
        <ellipse className="password-monkey__hand password-monkey__hand--right" cx="43" cy="33" rx="10" ry="7.5" fill="#8d7048" />
      </g>
    </svg>
  )
}

export function PasswordField({
  id,
  label,
  name,
  autoComplete,
  value,
  disabled,
  required = true,
  minLength,
  maxLength,
  onChange,
}: PasswordFieldProps): JSX.Element {
  const [visible, setVisible] = useState<boolean>(false)
  const toggleLabel: string = visible ? `${label} verbergen` : `${label} anzeigen`

  return (
    <>
      <label htmlFor={id}>{label}</label>
      <div className="password-field">
        <input
          id={id}
          name={name}
          type={visible ? 'text' : 'password'}
          autoComplete={autoComplete}
          required={required}
          minLength={minLength}
          maxLength={maxLength}
          value={value}
          disabled={disabled}
          spellCheck={false}
          onChange={onChange}
        />
        <button
          type="button"
          className={visible ? 'password-toggle password-toggle--open' : 'password-toggle'}
          aria-label={toggleLabel}
          aria-pressed={visible}
          disabled={disabled}
          onClick={() => setVisible((current: boolean): boolean => !current)}
        >
          <MonkeyIcon eyesOpen={visible} />
        </button>
      </div>
    </>
  )
}
