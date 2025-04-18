/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts,scss}",
  ],
  important: true, // Make Tailwind CSS classes have higher specificity
  safelist: [
    // Add classes that might be dynamically generated
    'bg-primary',
    'bg-primary-light',
    'text-primary',
    'bg-success',
    'bg-success-light',
    'text-success',
    'bg-error',
    'bg-error-light',
    'text-error',
    'translate-x-0',
    'translate-x-full',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a73e8',
          light: '#e8f0fe',
          dark: '#1765cc',
        },
        secondary: {
          DEFAULT: '#5f6368',
          light: '#f1f3f4',
          dark: '#202124',
        },
        success: {
          DEFAULT: '#1e8e3e',
          light: '#e6f4ea',
          dark: '#137333',
        },
        warning: {
          DEFAULT: '#f29900',
          light: '#fef7e0',
        },
        error: {
          DEFAULT: '#d93025',
          light: '#fce8e6',
          dark: '#c5221f',
        },
        neutral: {
          50: '#f8f9fa',
          100: '#f1f3f4',
          200: '#e8eaed',
          300: '#dadce0',
          400: '#bdc1c6',
          500: '#9aa0a6',
          600: '#5f6368',
          700: '#3c4043',
          800: '#202124',
          900: '#121212',
        }
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0,0,0,0.05)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.08)',
        'button': '0 2px 4px rgba(0,0,0,0.1)',
        'button-hover': '0 4px 8px rgba(0,0,0,0.15)',
      },
      fontFamily: {
        'google-sans': ['"Google Sans"', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'card': '12px',
        'button': '22px',
        'tag': '14px',
        'search': '24px',
      },
    },
  },
  plugins: [],
}
