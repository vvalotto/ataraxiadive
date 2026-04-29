interface EmptyStateCardProps {
  message: string
}

export function EmptyStateCard({ message }: EmptyStateCardProps) {
  return (
    <section className="rounded-[2rem] border border-slate-700 bg-slate-900/85 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.24)]">
      <div className="rounded-[1.75rem] border border-dashed border-slate-700 bg-slate-950/60 px-5 py-8 text-center">
        <p className="text-base font-semibold text-white">{message}</p>
      </div>
    </section>
  )
}
