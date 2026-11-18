"use client"; // Les frontières d'erreur sont forcément des composants client.

import { useEffect } from "react";
import { Button } from "@/components/ds/control";
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
            Données <Em>indisponibles</Em>.
          </>
        }
        intro="L’API n’a pas répondu ou a renvoyé une erreur. Les autres pages ne sont pas touchées."
      >
        <div className="mt-7 flex flex-wrap items-center gap-4">
          <Button variant="primary" onClick={() => unstable_retry()}>
            Réessayer
          </Button>
          {error.digest && <span className="font-mono text-[11px] text-muted-text">Référence : {error.digest}</span>}
        </div>
      </PageHero>
    </Page>
  );
}
