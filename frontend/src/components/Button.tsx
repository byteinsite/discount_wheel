import type { ReactNode } from "react";

type ButtonProps = {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: "primary" | "ghost";
};

export default function Button({
  children,
  onClick,
  disabled,
  loading,
  variant = "primary",
}: ButtonProps) {
  return (
    <button
      type="button"
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? "..." : children}
    </button>
  );
}
