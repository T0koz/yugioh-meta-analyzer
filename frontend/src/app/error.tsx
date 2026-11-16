"use client"; // Les frontières d'erreur sont forcément des composants client.

import { useEffect } from "react";
import { Em } from "@/components/ds/em";
import { Page, PageHero } from "@/components/ds/page";

// Next 16 : la prop de reprise s'appelle `unstable_retry` (elle relance le
// rendu serveur du segment, donc l'appel à l'API), et non plus `reset`.
export default function ErrorPage({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <Page>
      <PageHero
        eyebrow="Erreur"
        title={
          <>
            Les données ne <Em>répondent</Em> pas.
          </>
        }
        intro="L’API n’a pas répondu ou a renvoyé une erreur. Le reste du site n’est pas touché : réessaie dans un instant."
      >
        <div className="mt-7 flex flex-wrap items-center gap-4">
          <button
            type="button"
            onClick={() => unstable_retry()}
            className="rounded-[4px] border border-signal bg-signal px-[18px] py-[11px] text-[14px] font-medium text-on-signal transition-transform duration-[250ms] ease-[var(--ease)] motion-safe:hover:-translate-y-px"
          >
            Réessayer
          </button>
          {error.digest && <span className="font-mono text-[11px] text-muted-text">Référence : {error.digest}</span>}
        </div>
      </PageHero>
    </Page>
  );
}
