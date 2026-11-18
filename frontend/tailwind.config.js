/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        charcoal: {
          950: '#090A0C',
          900: '#111215',
          850: '#16181D',
          800: '#1C1F26',
          700: '#282C37',
          600: '#3B4151',
          500: '#525B6F',
        },
        forge: {
          cyan: '#00F0FF',
          accent: '#3B82F6',
          purple: '#8B5CF6',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#F43F5E'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
