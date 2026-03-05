/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        display: ['"Syne"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        yellow: {
          300: '#fde047',
          400: '#facc15',
          500: '#eab308',
          600: '#ca8a04',
        },
        emerald: {
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
        },
        red: {
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
        }
      }
    },
  },
  plugins: [],
}
