// Mot d'accent d'un titre (docs/design-system.md §3) : un seul par titre.
export function Em({ children }: { children: React.ReactNode }) {
  return <em className="font-serif italic font-normal text-signal tracking-[-0.01em]">{children}</em>;
}
