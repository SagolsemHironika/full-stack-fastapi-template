import { useEffect, useState } from "react"

export function useDebounce<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    setTimeout(() => setDebounced(value), delay)
  }, [value, delay])

  return debounced
}
