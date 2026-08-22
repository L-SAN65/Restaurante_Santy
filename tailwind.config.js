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
        // Haute Management — DESIGN.md (Corporate Modern Minimalist)
        primary: {
          DEFAULT: "#000000",
          hover: "#1b1b1c",
          soft: "#e5e2e3",
          deep: "#1b1b1c",
          container: "#1b1b1c",
          fixed: "#e5e2e3",
          fixedDim: "#c8c6c7",
        },
        secondary: {
          DEFAULT: "#735c00",
          container: "#fed65b",
          fixed: "#ffe088",
          fixedDim: "#e9c349",
        },
        warning: {
          DEFAULT: "#735c00",
          soft: "#ffe088",
        },
        danger: {
          DEFAULT: "#ba1a1a",
          container: "#ffdad6",
        },
        info: {
          DEFAULT: "#5f5e5f",
        },
        surface: {
          bg: "#fbf9f4",
          card: "#FFFFFF",
          dim: "#dbdad5",
          bright: "#fbf9f4",
          containerLowest: "#ffffff",
          containerLow: "#f5f3ee",
          container: "#f0eee9",
          containerHigh: "#eae8e3",
          containerHighest: "#e4e2dd",
          variant: "#e4e2dd",
          tint: "#5f5e5f",
        },
        text: {
          primary: "#1b1c19",
          secondary: "#46474a",
          variant: "#46474a",
        },
        outline: {
          DEFAULT: "#76777b",
          variant: "#c7c6ca",
        },
        mesa: {
          reservada: "#60A5FA",
          ocupada: "#F59E0B",
          disponible: "#BBF7D0",
          bloqueada: "rgba(186, 26, 26, 0.08)",
          inactiva: "#e4e2dd",
        },
        kds: {
          ok: "#735c00",
          warn: "#e9c349",
          over: "#ba1a1a",
          bg: "#1b1b1c",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Playfair Display", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      borderRadius: {
        sm: "0.25rem",
        DEFAULT: "0.5rem",
        component: "8px",
        md: "0.75rem",
        card: "12px",
        lg: "1rem",
        xl: "1.5rem",
        badge: "9999px",
      },
      boxShadow: {
        card: "0 1px 2px rgba(27,28,25,0.06), 0 1px 8px rgba(27,28,25,0.04)",
        modal: "0 12px 24px rgba(27,28,25,0.12), 0 4px 8px rgba(27,28,25,0.08)",
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