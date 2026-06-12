export function Spinner() {
  return <span className="spinner" aria-label="Loading" />
}

export function LoadingScreen({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="center-screen">
      <div className="stack--sm" style={{ alignItems: 'center', gap: 12 }}>
        <Spinner />
        <span className="muted">{label}</span>
      </div>
    </div>
  )
}
