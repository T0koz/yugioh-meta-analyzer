"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import { fmtNum } from "@/lib/format";

// Embellissements de l'accueil. Chacun part d'un HTML serveur complet et
// lisible : sans JavaScript ou en mouvement réduit, ces composants ne font rien.

const motionOk = () => window.matchMedia("(prefers-reduced-motion: no-preference)").matches;
const clamp = (v: number) => Math.max(0, Math.min(1, v));

/** Braises du hero : canvas 2D, en pause hors écran et onglet caché. */
export function Embers({ className = "" }: { className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx || !motionOk()) return;

    const css = getComputedStyle(canvas);
    const hot = css.getPropertyValue("--signal-hi").trim();
    const cold = css.getPropertyValue("--soft").trim();
    const particles = Array.from({ length: 60 }, () => ({
      x: Math.random(),
      y: Math.random(),
      r: 0.6 + Math.random() * 1.6,
      v: 0.00025 + Math.random() * 0.0007,
      phase: Math.random() * 6.28,
    }));
    let width = 0;
    let height = 0;
    let visible = true;
    let frame = 0;

    const size = () => {
      const dpr = Math.min(window.devicePixelRatio, 2);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const draw = (t: number) => {
      frame = requestAnimationFrame(draw);
      if (!visible || document.hidden) return;
      ctx.clearRect(0, 0, width, height);
      for (const p of particles) {
        p.y -= p.v;
        if (p.y < -0.02) {
          p.y = 1.02;
          p.x = Math.random();
        }
        const alpha = 0.12 + 0.3 * (0.5 + 0.5 * Math.sin(t / 900 + p.phase));
        ctx.globalAlpha = p.r > 1.7 ? alpha : alpha * 0.6;
        ctx.fillStyle = p.r > 1.7 ? hot : cold;
        ctx.beginPath();
        ctx.arc((p.x + Math.sin(t / 2400 + p.phase) * 0.012) * width, p.y * height, p.r, 0, 6.28);
        ctx.fill();
      }
    };
    const observer = new IntersectionObserver(([entry]) => (visible = entry.isIntersecting));

    size();
    window.addEventListener("resize", size);
    observer.observe(canvas);
    frame = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener("resize", size);
    };
  }, []);

  return <canvas ref={ref} aria-hidden className={className} />;
}

/** Scène de l'éventail : l'inclinaison et le reflet suivent le pointeur. */
export function FanStage({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stage = ref.current;
    if (!stage || !motionOk() || !window.matchMedia("(hover: hover)").matches) return;
    const move = (e: PointerEvent) => {
      const r = stage.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      stage.style.setProperty("--ry", `${-14 + x * 26}deg`);
      stage.style.setProperty("--rx", `${8 - y * 18}deg`);
      stage.style.setProperty("--sx", `${30 + x * 80}%`);
      stage.style.setProperty("--sy", `${30 + y * 80}%`);
    };
    const leave = () => ["--ry", "--rx", "--sx", "--sy"].forEach((v) => stage.style.removeProperty(v));
    stage.addEventListener("pointermove", move);
    stage.addEventListener("pointerleave", leave);
    return () => {
      stage.removeEventListener("pointermove", move);
      stage.removeEventListener("pointerleave", leave);
    };
  }, []);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}

/** Nombre qui compte une fois, à son entrée dans l'écran. Le HTML serveur porte la valeur finale. */
export function CountUp({ value, digits = 0 }: { value: number; digits?: number }) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !motionOk()) return;
    let frame = 0;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        observer.disconnect();
        const start = performance.now();
        const tick = (t: number) => {
          const p = Math.min(1, (t - start) / 1200);
          el.textContent = fmtNum(value * (1 - Math.pow(1 - p, 4)), digits);
          if (p < 1) frame = requestAnimationFrame(tick);
        };
        frame = requestAnimationFrame(tick);
      },
      { threshold: 0.25 }
    );
    observer.observe(el);
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
      el.textContent = fmtNum(value, digits);
    };
  }, [value, digits]);

  return <span ref={ref}>{fmtNum(value, digits)}</span>;
}

/** Tuile-lien du bento : pose --mx / --my pour la lueur qui suit le pointeur (CSS : .home-tile). */
export function GlowLink({ href, className = "", children }: { href: string; className?: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className={`home-tile ${className}`}
      onPointerMove={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        e.currentTarget.style.setProperty("--mx", `${e.clientX - r.left}px`);
        e.currentTarget.style.setProperty("--my", `${e.clientY - r.top}px`);
      }}
    >
      {children}
    </Link>
  );
}

/**
 * Récit au défilement de « la preuve ». Sur grand écran et si le mouvement est
 * autorisé, pose `data-live` (le CSS épingle alors le graphique) puis relie le
 * tracé des courbes à la progression du défilement. Sinon : section statique.
 */
export function ProofScroll({
  children,
  className = "",
  ...rest
}: { children: React.ReactNode; className?: string; id?: string; "aria-labelledby"?: string }) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const queries = ["(prefers-reduced-motion: no-preference)", "(min-width: 900px)", "(min-height: 620px)"].map((q) =>
      window.matchMedia(q)
    );
    let live = false;
    let frame = 0;

    const render = () => {
      frame = 0;
      const rect = el.getBoundingClientRect();
      const p = clamp(-rect.top / (rect.height - window.innerHeight));
      el.style.setProperty("--ocg-off", String(1 - clamp(p / 0.3)));
      el.style.setProperty("--tcg-off", String(1 - clamp((p - 0.33) / 0.3)));
      el.dataset.step = p < 0.33 ? "0" : p < 0.66 ? "1" : "2";
      el.toggleAttribute("data-ocg", p > 0.28);
      el.toggleAttribute("data-tcg", p > 0.6);
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(render);
    };
    const stop = () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(frame);
      frame = 0;
      ["data-live", "data-step", "data-ocg", "data-tcg"].forEach((a) => el.removeAttribute(a));
      el.style.removeProperty("--ocg-off");
      el.style.removeProperty("--tcg-off");
    };
    const sync = () => {
      const want = queries.every((q) => q.matches);
      if (want === live) return;
      live = want;
      if (!live) return stop();
      el.setAttribute("data-live", "");
      window.addEventListener("scroll", onScroll, { passive: true });
      render();
    };

    sync();
    queries.forEach((q) => q.addEventListener("change", sync));
    return () => {
      queries.forEach((q) => q.removeEventListener("change", sync));
      stop();
    };
  }, []);

  return (
    <section ref={ref} className={`home-proof ${className}`} {...rest}>
      {children}
    </section>
  );
}
