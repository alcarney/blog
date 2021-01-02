module.exports = {
  purge: [
    "./layouts/**/*.html"
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      typography: (theme) => ({
        DEFAULT: {
          css: {
            h1: {
              fontWeight: '500',
              color: theme('colors.green.600')
            },
            h2: {
              fontWeight: '500',
            },
            h3: {
              fontWeight: '500',
            },
            h4: {
              fontWeight: '500',
            },
            pre: {
              color: 'rgb(88, 110, 117)',
              backgroundColor: '#fdf6e3'
            },
            'pre code::before': {
              display: 'none',
            },
            'pre code::after': {
              display: 'none',
            },
            'td > pre': {
              margin: 0,
              paddingLeft: '0',
              boxShadow: 'none'
            }
          }
        },
        lg: {
          css: {
            h1: {
              fontSize: '1.875rem',
            },
            pre: {
              //border: 'solid 1px #e5e7eb',
              borderRadius: '2px',
              boxShadow: 'var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
            }
          }
        }
      })
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography')
  ],
}
