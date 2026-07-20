export type MeResponse = {
  name: string;
  spinned: boolean;
  telegram_id: number;
};

export type AuthResponse = {
  ok: boolean;
  telegram_id: number;
  name: string;
  spinned: boolean;
};

export type SpinResponse = {
  discount: number;
  promo: string | null;
  angle: number;
};

export type ResultResponse = {
  discount: number;
  promo: string | null;
};

function getInitData(): string {
  const tg = window.Telegram?.WebApp;
  if (tg?.initData) {
    return tg.initData;
  }
  // Local browser fallback (backend ALLOW_DEV_AUTH=true)
  const params = new URLSearchParams({
    user: JSON.stringify({
      id: 10001,
      first_name: "Dev",
      last_name: "User",
      username: "devuser",
    }),
    auth_date: String(Math.floor(Date.now() / 1000)),
  });
  return `dev=1&${params.toString()}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const initData = getInitData();
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `tma ${initData}`);
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(path, { ...init, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = (await res.json()) as { detail?: string };
      if (data.detail) detail = data.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export const api = {
  auth: () =>
    request<AuthResponse>("/auth", {
      method: "POST",
      body: JSON.stringify({ initData: getInitData() }),
    }),
  me: () => request<MeResponse>("/me"),
  spin: () => request<SpinResponse>("/spin", { method: "POST" }),
  result: () => request<ResultResponse>("/result"),
};

export { getInitData };
