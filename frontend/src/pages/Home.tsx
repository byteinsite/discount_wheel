import { useEffect, useState } from "react";
import { api, type ResultResponse, type SpinResponse } from "../api";
import Button from "../components/Button";
import Wheel from "../components/Wheel";

type Status = "loading" | "ready" | "spinning" | "done" | "error";

export default function Home() {
  const [status, setStatus] = useState<Status>("loading");
  const [name, setName] = useState("");
  const [rotation, setRotation] = useState(0);
  const [result, setResult] = useState<Pick<SpinResponse, "discount" | "promo"> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    tg?.ready();
    tg?.expand();
    tg?.setHeaderColor?.("#0b1f18");
    tg?.setBackgroundColor?.("#0b1f18");

    let cancelled = false;

    (async () => {
      try {
        const auth = await api.auth();
        if (cancelled) return;
        setName(auth.name);

        if (auth.spinned) {
          const existing: ResultResponse = await api.result();
          if (cancelled) return;
          setResult({ discount: existing.discount, promo: existing.promo });
          setStatus("done");
          return;
        }

        setStatus("ready");
      } catch (e) {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Ошибка загрузки");
        setStatus("error");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSpin() {
    if (status !== "ready") return;
    setError(null);
    setStatus("spinning");
    window.Telegram?.WebApp?.HapticFeedback?.impactOccurred("medium");

    try {
      const data = await api.spin();
      // Animate to server-provided angle
      setRotation(data.angle);

      window.setTimeout(() => {
        setResult({ discount: data.discount, promo: data.promo });
        setStatus("done");
        window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred(
          data.discount > 0 ? "success" : "warning",
        );
      }, 4800);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось крутить");
      setStatus("ready");
    }
  }

  return (
    <main className="app">
      <div className="atmosphere" aria-hidden />
      <header className="header">
        <p className="brand">Lucky Spin</p>
        <h1 className="title">Колесо скидок</h1>
        {name ? <p className="subtitle">Привет, {name}! Крути и забери свою скидку.</p> : null}
      </header>

      <Wheel rotation={rotation} spinning={status === "spinning"} />

      <section className="panel" aria-live="polite">
        {status === "loading" && <p className="hint">Подключаемся к Telegram…</p>}

        {status === "error" && (
          <>
            <p className="hint error">{error}</p>
            <Button onClick={() => window.location.reload()}>Повторить</Button>
          </>
        )}

        {status === "ready" && (
          <>
            <p className="hint">Одно вращение на аккаунт. Удачи!</p>
            <Button onClick={handleSpin}>Крутить колесо</Button>
          </>
        )}

        {status === "spinning" && <p className="hint">Колесо крутится…</p>}

        {status === "done" && result && (
          <div className="result">
            {result.discount > 0 ? (
              <>
                <p className="result-label">Ваша скидка</p>
                <p className="result-value">{result.discount}%</p>
                {result.promo ? (
                  <p className="promo">
                    Промокод: <code>{result.promo}</code>
                  </p>
                ) : null}
              </>
            ) : (
              <>
                <p className="result-label">Без выигрыша</p>
                <p className="hint">В этот раз не повезло — попробуйте в следующей акции.</p>
              </>
            )}
            {error ? <p className="hint error">{error}</p> : null}
          </div>
        )}
      </section>
    </main>
  );
}
