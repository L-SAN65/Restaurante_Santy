/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./core/templates/**/*.html",
    "./reservations/templates/**/*.html",
    "./billing/templates/**/*.html",
    "./kitchen/templates/**/*.html",
    "./inventory/templates/**/*.html",
    "./loyalty/templates/**/*.html",
    "./audit/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        // Sistema de diseño Stitch (DESIGN.md)
        primary: {
          DEFAULT: "#22C55E",
          hover: "#16A34A",
          soft: "#BBF7D0",
          deep: "#166534",
        },
        warning: {
          DEFAULT: "#FACC15",
        },
        danger: {
          DEFAULT: "#EF4444",
        },
        info: {
          DEFAULT: "#3B82F6",
        },
        surface: {
          bg: "#F8FAFC",
          card: "#FFFFFF",
        },
        text: {
          primary: "#1E293B",
          secondary: "#94A3B8",
        },
        mesa: {
          reservada: "#60A5FA",
          ocupada: "#F59E0B",
          disponible: "#BBF7D0",
          bloqueada: "rgba(239, 68, 68, 0.3)",
          inactiva: "#E2E8F0",
        },
        kds: {
          ok: "#22C55E",
          warn: "#FACC15",
          over: "#EF4444",
          bg: "#111827",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      borderRadius: {
        component: "8px",
        card: "12px",
        badge: "9999px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06)",
        modal: "0 10px 40px rgba(0,0,0,0.25)",
      },
      keyframes: {
        "fade-scale": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-scale": "fade-scale 0.2s ease-out",
        "slide-up": "slide-up 0.25s ease-out",
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};