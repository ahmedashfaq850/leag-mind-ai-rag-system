interface SourceCitationsProps {
  sources: string[];
}

export function SourceCitations({ sources }: SourceCitationsProps) {
  if (!sources?.length) return null;

  return (
    <div className="mt-5 pt-4 border-t border-stone-100">
      <p className="text-xs font-semibold text-stone-500 uppercase tracking-wider mb-3">
        Sources ({sources.length})
      </p>
      <div className="flex flex-wrap gap-2">
        {sources.map((name, i) => (
          <span
            key={i}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-100 text-sm font-medium"
          >
            <span className="text-amber-600">{i + 1}</span>
            <span className="font-mono text-xs">{name}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
