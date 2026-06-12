import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}
interface State {
  error: Error | null
}

/** Catches render errors so a single broken page shows a message instead of a
 *  blank white screen, and surfaces the actual error for diagnosis. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error('Render error:', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="center-screen">
          <div className="card" style={{ maxWidth: 620 }}>
            <div className="card__body stack--sm">
              <div className="banner banner--warning">
                <span className="banner__icon">⚠</span>
                <div>
                  <strong>This view hit an error while rendering.</strong>
                  <div style={{ marginTop: 6, fontSize: 13, fontFamily: 'var(--font-mono)' }}>
                    {this.state.error.message}
                  </div>
                </div>
              </div>
              <button className="btn btn--primary" onClick={() => this.setState({ error: null })}>
                ↻ Try again
              </button>
            </div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
