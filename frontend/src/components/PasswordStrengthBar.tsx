type Strength = 'debil' | 'buena' | 'fuerte'

function getStrength(password: string): Strength {
  const meetsPolicy =
    password.length >= 10 && /[A-Z]/.test(password) && /[0-9]/.test(password)
  if (!meetsPolicy) return 'debil'
  if (password.length >= 14) return 'fuerte'
  return 'buena'
}

const CONFIG: Record<Strength, { label: string; bar: string; text: string }> = {
  debil:  { label: 'Débil',  bar: 'w-1/3 bg-red-500',    text: 'text-red-400'    },
  buena:  { label: 'Buena',  bar: 'w-2/3 bg-yellow-400', text: 'text-yellow-400' },
  fuerte: { label: 'Fuerte', bar: 'w-full bg-green-500',  text: 'text-green-400'  },
}

export function PasswordStrengthBar({ password }: { password: string }) {
  if (!password) return null
  const { label, bar, text } = CONFIG[getStrength(password)]
  return (
    <div className="mt-2">
      <div className="h-1 w-full overflow-hidden rounded-full bg-slate-700">
        <div className={`h-1 rounded-full transition-all duration-300 ${bar}`} />
      </div>
      <span className={`mt-1 block text-xs ${text}`}>{label}</span>
    </div>
  )
}
