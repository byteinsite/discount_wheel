import { useMemo } from "react";

/** Must match backend WHEEL_SEGMENTS order */
export const WHEEL_SEGMENTS = [5, 10, 15, 20, 25, 30, 0] as const;

const COLORS = [
  "#1a6b4a",
  "#f0c75e",
  "#0f3d2e",
  "#e8a838",
  "#248f63",
  "#d4922a",
  "#163d30",
];

type WheelProps = {
  rotation: number;
  spinning: boolean;
};

function labelFor(discount: number): string {
  return discount === 0 ? "—" : `${discount}%`;
}

export default function Wheel({ rotation, spinning }: WheelProps) {
  const gradient = useMemo(() => {
    const n = WHEEL_SEGMENTS.length;
    const step = 360 / n;
    const parts = WHEEL_SEGMENTS.map((_, i) => {
      const start = i * step;
      const end = (i + 1) * step;
      return `${COLORS[i % COLORS.length]} ${start}deg ${end}deg`;
    });
    return `conic-gradient(from -90deg, ${parts.join(", ")})`;
  }, []);

  return (
    <div className="wheel-stage">
      <div className="wheel-pointer" aria-hidden />
      <div
        className={`wheel ${spinning ? "wheel-spinning" : ""}`}
        style={{
          background: gradient,
          transform: `rotate(${rotation}deg)`,
        }}
        role="img"
        aria-label="Колесо скидок"
      >
        <svg className="wheel-labels" viewBox="0 0 200 200">
          {WHEEL_SEGMENTS.map((discount, i) => {
            const n = WHEEL_SEGMENTS.length;
            const step = 360 / n;
            const angle = -90 + i * step + step / 2;
            const rad = (angle * Math.PI) / 180;
            const r = 68;
            const x = 100 + r * Math.cos(rad);
            const y = 100 + r * Math.sin(rad);
            return (
              <text
                key={`${discount}-${i}`}
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                transform={`rotate(${angle + 90}, ${x}, ${y})`}
                className="wheel-label"
              >
                {labelFor(discount)}
              </text>
            );
          })}
        </svg>
        <div className="wheel-hub">
          <span>SPIN</span>
        </div>
      </div>
      <div className="wheel-glow" aria-hidden />
    </div>
  );
}
