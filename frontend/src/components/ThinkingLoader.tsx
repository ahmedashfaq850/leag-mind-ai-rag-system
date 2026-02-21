export function ThinkingLoader() {
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="flex gap-1.5">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 rounded-full bg-amber-500 animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 rounded-full bg-amber-600 animate-bounce" />
      </div>
      <span className="text-sm text-stone-500">Searching documents...</span>
    </div>
  );
}
