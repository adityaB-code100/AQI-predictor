    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            primary: {
              50: '#f0f9ff',
              100: '#e0f2fe',
              200: '#bae6fd',
              300: '#7dd3fc',
              400: '#38bdf8',
              500: '#0ea5e9',
              600: '#0284c7',
              700: '#0369a1',
              800: '#075985',
              900: '#0c4a6e',
            },
            secondary: {
              50: '#f0fdf4',
              100: '#dcfce7',
              200: '#bbf7d0',
              300: '#86efac',
              400: '#4ade80',
              500: '#22c55e',
              600: '#16a34a',
              700: '#15803d',
              800: '#166534',
              900: '#14532d',
            }
          },
          animation: {
            'fadeIn': 'fadeIn 0.6s forwards',
            'pulse': 'pulse 2s infinite',
            'slideInRight': 'slideInRight 0.5s forwards',
            'fadeOut': 'fadeOut 0.5s forwards',
            'float': 'float 6s ease-in-out infinite',
            'spin-slow': 'spin 3s linear infinite',
            'bounce-slow': 'bounce 2s infinite',
            'shimmer': 'shimmer 2s infinite',
          },
          keyframes: {
            fadeIn: {
              from: { opacity: 0, transform: 'translateY(20px)' },
              to: { opacity: 1, transform: 'translateY(0)' }
            },
            slideInRight: {
              from: { transform: 'translateX(100%)', opacity: 0 },
              to: { transform: 'translateX(0)', opacity: 1 }
            },
            fadeOut: {
              to: { opacity: 0, transform: 'translateX(100%)' }
            },
            float: {
              '0%, 100%': { transform: 'translateY(0)' },
              '50%': { transform: 'translateY(-10px)' }
            },
            shimmer: {
              '0%': { backgroundPosition: '-468px 0' },
              '100%': { backgroundPosition: '468px 0' }
            }
          }
        }
      }
    }
  