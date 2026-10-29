/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: '#0F1A14',
        moss: '#0B6B3A',
        mint: '#E6F2EA',
        sand: '#F7F5EF',
        'kenya-green': '#006600',
        'kenya-red': '#BB0000',
        'kenya-black': '#000000',
      }
    },
  },
  plugins: [],
}