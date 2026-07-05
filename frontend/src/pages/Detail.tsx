import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getUniversityDetail, getMajorDetail } from '../api'
import type { UniversityDetail, MajorInfo } from '../types'

export default function Detail() {
  const { type, id } = useParams<{ type: string; id: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [uni, setUni] = useState<UniversityDetail | null>(null)
  const [major, setMajor] = useState<MajorInfo | null>(null)

  useEffect(() => {
    if (!type || !id) return
    setLoading(true)
    const numId = parseInt(id)
    if (type === 'university') {
      getUniversityDetail(numId)
        .then(setUni)
        .catch(() => {})
        .finally(() => setLoading(false))
    } else if (type === 'major') {
      getMajorDetail(numId)
        .then(setMajor)
        .catch(() => {})
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [type, id])

  if (loading) {
    return <div className="card"><div className="loading"><div className="spinner" /><p className="mt-2">加载详情...</p></div></div>
  }

  if (uni) return <UniversityView uni={uni} onBack={() => navigate(-1)} />
  if (major) return <MajorView major={major} onBack={() => navigate(-1)} />

  return (
    <div className="card">
      <div className="empty-state">
        <p>😕 未找到相关信息</p>
        <button className="btn btn-outline mt-4" onClick={() => navigate(-1)}>← 返回</button>
      </div>
    </div>
  )
}

function UniversityView({ uni, onBack }: { uni: UniversityDetail; onBack: () => void }) {
  return (
    <div>
      <button className="btn btn-outline btn-sm mb-4" onClick={onBack}>← 返回</button>

      <div className="detail-header">
        <h1>
          {uni.name}
          <span className={`school-tier tier-${uni.tier}`}>{uni.tier}</span>
          {uni.is_double_first_class && <span className="school-tier tier-双一流">双一流</span>}
        </h1>
        <p className="text-muted mt-2">
          📍 {uni.province} {uni.city} · {uni.type}类 · 就业率 {Math.round(uni.avg_employment_rate * 100)}%
        </p>
        <p className="mt-2">{uni.description}</p>
      </div>

      {/* Admission Trends */}
      <div className="card">
        <h2>📈 历年录取分数线趋势</h2>
        {uni.admission_trends.length > 0 && (
          <div className="mt-4">
            {uni.admission_trends.map(t => (
              <div key={t.year} className="chart-bar-row" style={{ marginBottom: 12 }}>
                <div className="label">{t.year}</div>
                <div className="track">
                  <div
                    className="fill progress-blue"
                    style={{
                      width: `${((t.avg_score - 500) / 250) * 100}%`,
                    }}
                  >
                    {t.avg_score}
                  </div>
                </div>
                <span className="text-muted" style={{ marginLeft: 10, fontSize: '.78rem' }}>
                  {t.min_score} ~ {t.max_score}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Majors */}
      <div className="card">
        <h2>📚 开设专业 ({uni.majors.length})</h2>
        <div className="grid-2 mt-4">
          {uni.majors.map(m => (
            <div key={m.id} className="rec-card" style={{ borderLeft: m.is_key_major ? '4px solid var(--primary)' : '4px solid var(--border)' }}>
              <div className="flex-between">
                <strong>{m.name}</strong>
                {m.is_key_major && <span className="tag" style={{ color: 'var(--primary)', fontWeight: 600 }}>重点学科</span>}
              </div>
              <div className="uni-meta">{m.category} · 前景 {m.prospect_score}/10 · 均薪 ¥{m.avg_salary.toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function MajorView({ major, onBack }: { major: MajorInfo; onBack: () => void }) {
  return (
    <div>
      <button className="btn btn-outline btn-sm mb-4" onClick={onBack}>← 返回</button>

      <div className="detail-header">
        <h1>{major.name}</h1>
        <p className="text-muted mt-2">专业代码: {major.code} · 大类: {major.category}</p>
        <p className="mt-2">{major.description}</p>
      </div>

      <div className="card">
        <h2>📊 专业数据概览</h2>
        <div className="detail-grid">
          <div className="detail-stat">
            <div className="value">¥{major.avg_salary.toLocaleString()}</div>
            <div className="label">平均薪资</div>
          </div>
          <div className="detail-stat">
            <div className="value">{Math.round(major.employment_rate * 100)}%</div>
            <div className="label">就业率</div>
          </div>
          <div className="detail-stat">
            <div className="value">{major.prospect_score}/10</div>
            <div className="label">前景评分</div>
          </div>
        </div>

        <div className="mt-4">
          <h3>🔑 相关关键词</h3>
          <div className="flex-center mt-2" style={{ flexWrap: 'wrap' }}>
            {major.keywords.split(',').map((kw, i) => (
              <span key={i} className="tag">{kw.trim()}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
