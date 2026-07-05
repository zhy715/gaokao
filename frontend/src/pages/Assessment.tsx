import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import type { AppState } from '../App'
import { getQuestions, submitAssessment } from '../api'
import type { AssessmentQuestion, AssessmentResult } from '../types'

interface Props {
  state: AppState
  updateState: (p: Partial<AppState>) => void
}

export default function Assessment({ updateState }: Props) {
  const navigate = useNavigate()
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([])
  const [answers, setAnswers] = useState<number[]>([])
  const [result, setResult] = useState<AssessmentResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getQuestions()
      .then(qs => {
        setQuestions(qs)
        setAnswers(new Array(qs.length).fill(-1))
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const allAnswered = answers.every(a => a >= 0)

  const handleSubmit = async () => {
    if (!allAnswered) return
    setLoading(true)
    try {
      const res = await submitAssessment(answers)
      setResult(res)
      updateState({
        assessmentScores: res.scores,
      })
    } catch {} finally { setLoading(false) }
  }

  const handleSelect = (qIdx: number, optIdx: number) => {
    const next = [...answers]
    next[qIdx] = optIdx
    setAnswers(next)
  }

  const progress = allAnswered ? 100 : Math.round((answers.filter(a => a >= 0).length / questions.length) * 100)

  if (loading) {
    return <div className="card"><div className="loading"><div className="spinner" /><p className="mt-2">加载测评题目...</p></div></div>
  }

  return (
    <div>
      <div className="steps">
        <div className="step done">① 输入分数</div>
        <div className="step active">② 兴趣测评</div>
        <div className="step">③ 查看推荐</div>
      </div>

      <div className="card">
        <div className="flex-between mb-4">
          <h2>🧠 专业兴趣测评</h2>
          <span className="text-muted">{answers.filter(a => a >= 0).length} / {questions.length} 题</span>
        </div>
        <div className="progress-bar mb-4">
          <div
            className="progress-bar-fill progress-blue"
            style={{ width: `${progress}%` }}
          />
        </div>

        {!result ? (
          <>
            {questions.map((q, qi) => (
              <div key={q.id} className="quiz-question">
                <h3>{q.id}. {q.question}</h3>
                {q.options.map((opt, oi) => (
                  <button
                    key={oi}
                    className={`quiz-option ${answers[qi] === oi ? 'selected' : ''}`}
                    onClick={() => handleSelect(qi, oi)}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            ))}

            <button
              className="btn btn-primary btn-lg mt-4"
              onClick={handleSubmit}
              disabled={!allAnswered}
            >
              {allAnswered ? '提交并查看结果' : `还有 ${questions.length - answers.filter(a => a >= 0).length} 题未答`}
            </button>
          </>
        ) : (
          <>
            <h3 className="mb-4">📊 测评结果</h3>
            <p className="text-muted mb-4">
              根据你的兴趣偏好，最匹配的专业方向是：
              <strong style={{ fontSize: '1.1rem', color: 'var(--primary)' }}>
                {' '}{result.primary_category?.name}
              </strong>
            </p>

            <div className="mb-4">
              {result.top_categories.map((cat, i) => (
                <div key={cat.code} className="chart-bar-row" style={{ marginBottom: 10 }}>
                  <div className="label">{cat.name}</div>
                  <div className="track">
                    <div
                      className={`fill ${i === 0 ? 'progress-blue' : i < 3 ? 'progress-green' : 'progress-orange'}`}
                      style={{ width: `${cat.score}%` }}
                    >
                      {cat.score > 0 && Math.round(cat.score)}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button
              className="btn btn-primary btn-lg"
              onClick={() => navigate('/results')}
            >
              查看志愿推荐 →
            </button>
          </>
        )}
      </div>
    </div>
  )
}
