/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/**/*.{html,js}", "./core/**/**/*.{html,js}", "./admin/**/**/*.{html,js}"],
  darkMode: 'selector',
  theme: {
    extend: {
      colors: {
        accent: '#0077b6',
        primary: '#38a3a5',

      }
    },
  },
  plugins: [],
}