export function InfoTooltip({ text }: { text: string }) {
  return (
    <span className="group relative inline-flex items-center ml-1 align-middle">
      <span className="cursor-help text-[10px] leading-none text-slate-500 hover:text-slate-300 border border-slate-600 rounded-full w-4 h-4 inline-flex items-center justify-center">
        ⓘ
      </span>
      <span className="pointer-events-none absolute left-1/2 -translate-x-1/2 top-full mt-2 hidden group-hover:block w-56 rounded-md bg-slate-800 border border-slate-700 px-3 py-2 text-xs font-normal normal-case text-slate-300 z-50 whitespace-normal shadow-lg">
        {text}
      </span>
    </span>
  );
}
