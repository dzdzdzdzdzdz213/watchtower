import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || '/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [org, setOrg] = useState(null)
  const [token, setToken] = useState(null)

  useEffect(() => {
    const t = localStorage.getItem('wt_token')
    const o = localStorage.getItem('wt_org')
    if (t && o) {
      setToken(t)
      setOrg(JSON.parse(o))
    }
  }, [])

  function login(email, password) {
    return axios.post(`${API}/auth/login`, { email, password }).then(({ data }) => {
      localStorage.setItem('wt_token', data.token)
      localStorage.setItem('wt_org', JSON.stringify(data.org))
      setToken(data.token)
      setOrg(data.org)
      return data
    })
  }

  function register(name, email, password) {
    return axios.post(`${API}/auth/register`, { name, email, password }).then(({ data }) => {
      localStorage.setItem('wt_token', data.token)
      localStorage.setItem('wt_org', JSON.stringify(data.org))
      setToken(data.token)
      setOrg(data.org)
      return data
    })
  }

  function logout() {
    localStorage.removeItem('wt_token')
    localStorage.removeItem('wt_org')
    setToken(null)
    setOrg(null)
  }

  return (
    <AuthContext.Provider value={{ org, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
