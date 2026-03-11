import { useEffect, useState } from 'react'

export function useMembers() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/members')
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
  }, [])

  return { data, loading }
}