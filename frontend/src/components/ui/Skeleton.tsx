interface TableSkeletonProps {
  columns: number
  rows?: number
}

// Column widths cycle so the placeholder reads like real tabular data instead
// of a uniform gray grid.
const CELL_WIDTHS = ['62%', '80%', '45%', '70%', '55%', '38%']

export function TableSkeleton({ columns, rows = 4 }: TableSkeletonProps) {
  return (
    <div className="skeleton-table" role="status" aria-label="Loading">
      {Array.from({ length: rows }).map((_, r) => (
        <div className="skeleton-row" key={r}>
          {Array.from({ length: columns }).map((_, c) => (
            <div
              className="skeleton skeleton-cell"
              key={c}
              style={{ width: CELL_WIDTHS[c % CELL_WIDTHS.length], flex: c === 1 ? 2 : 1 }}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

export function PagePreviewSkeleton() {
  const widths = ['48%', '90%', '82%', '86%', '70%', '78%', '64%', '88%', '58%']
  return (
    <div className="skeleton-page" role="status" aria-label="Building preview">
      {widths.map((w, i) => (
        <div
          className="skeleton"
          key={i}
          style={{ width: w, height: i === 0 ? 18 : 11, marginBottom: i === 0 ? 12 : 0 }}
        />
      ))}
    </div>
  )
}
