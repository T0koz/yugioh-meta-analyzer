export function InfoTooltip({ text }: { text: string }) {
  return (
    <span className="group relative ml-1 inline-flex items-center align-middle normal-case tracking-normal">
      <span
        tabIndex={0}
        className="inline-flex h-4 w-4 cursor-help items-center justify-center rounded-full border border-line-2 font-sans text-[10px] leading-none text-muted-text transition-colors duration-200 hover:text-text"
      >
        ⓘ
      </span>
      <span className="pointer-events-none absolute top-full left-1/2 z-50 mt-2 hidden w-60 -translate-x-1/2 rounded-[4px] border border-line-2 bg-ink-3 px-3 py-2.5 font-sans text-[12px] leading-[1.5] font-normal whitespace-normal text-soft group-hover:block group-focus-within:block">
        {text}
      </span>
    </span>
  );
}
