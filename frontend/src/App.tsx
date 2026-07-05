import { useState } from 'react'
import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import Home from './pages/Home'
import Assessment from './pages/Assessment'
import Results from './pages/Results'
import Detail from './pages/Detail'

export interface AppState {
  province: string
  score: number
  category: string
  assessmentScores: Record<string, number> | null
}

function App() {
  const navigate = useNavigate()
  const [state, setState] = useState<AppState>({
    province: '北京',
    score: 620,
    category: '理科',
    assessmentScores: null,
  })

  const updateState = (partial: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...partial }))
  }

  return (
    <>
      <header className="app-header">
        <div className="container">
          <h1 onClick={() => navigate('/')}>🎓 智能高考志愿填报</h1>
          <nav>
            <Link to="/">📝 分数输入</Link>
            <Link to="/assessment">🧠 兴趣测评</Link>
            <Link to="/results">📊 推荐结果</Link>
          </nav>
        </div>
      </header>

      <main>
        <div className="container">
          <Routes>
            <Route path="/" element={<Home state={state} updateState={updateState} />} />
            <Route path="/assessment" element={<Assessment state={state} updateState={updateState} />} />
            <Route path="/results" element={<Results state={state} />} />
            <Route path="/detail/:type/:id" element={<Detail />} />
          </Routes>
        </div>
      </main>
    </>
  )
}

export default App
