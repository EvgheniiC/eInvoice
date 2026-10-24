import { createContext, useContext, type JSX, type MouseEvent, type ReactNode } from 'react'

type FollowPath = (path: string) => void

const FollowPathContext: React.Context<FollowPath> = createContext<FollowPath>(() => {})

type FollowPathProviderProps = {
  followPath: FollowPath
  children: ReactNode
}

export function FollowPathProvider({
  followPath,
  children,
}: FollowPathProviderProps): JSX.Element {
  return <FollowPathContext.Provider value={followPath}>{children}</FollowPathContext.Provider>
}

type AppLinkProps = {
  href: string
  className?: string
  children: ReactNode
  'aria-label'?: string
}

export function AppLink({
  href,
  className,
  children,
  'aria-label': ariaLabel,
}: AppLinkProps): JSX.Element {
  const followPath: FollowPath = useContext(FollowPathContext)

  function onClick(event: MouseEvent<HTMLAnchorElement>): void {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return
    }
    event.preventDefault()
    followPath(href)
  }

  return (
    <a href={href} className={className} aria-label={ariaLabel} onClick={onClick}>
      {children}
    </a>
  )
}
