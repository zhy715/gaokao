import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import type { AppState } from '../App'
import { getRecommendations, getMajorCategories } from '../api'
import type { RecommendationResponse, RecommendationItem, MajorCategory } from '../types'

const TIER_LABELS: Record<string, { label: string; cls: string }> = {
  reach: { label: '🔴 冲刺', cls: 'tier-badge-reach' },
  match: { label: '🟡 稳妥', cls: 'tier-badge-match' },
  safety: { label: '🟢 保底', cls: 'tier-badge-safety' },
}

interface Props {
  state: AppState
}

export default function Results({ state }: Props) {
  const navigate = useNavigate()
  const [data, setData] = useState<RecommendationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'reach' | 'match' | 'safety'>('match')
  const [categories, setCategories] = useState<MajorCategory[]>([])

  // Filters
  const [filterTier, setFilterTier] = useState('')
  const [filterCity, setFilterCity] = useState('')
  const [filterMajorCat, setFilterMajorCat] = useState('')

  useEffect(() => {
    getMajorCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError('')
    getRecommendations({
      province: state.province,
      score: state.score,
      category: state.category,
      assessment_scores: state.assessmentScores,
    })
      .then(setData)
      .catch(() => setError('无法获取推荐结果，请确保后端已启动'))
      .finally(() => setLoading(false))
  }, [state.province, state.score, state.category, state.assessmentScores])

  // Deduplicate by university+major
  const allItems = useMemo(() => {
    if (!data) return { reach: [], match: [], safety: [] }
    const dedup = (items: RecommendationItem[]) => {
      const seen = new Set<string>()
      return items.filter(it => {
        const key = `${it.university.id}-${it.major.id}`
        if (seen.has(key)) return false
        seen.add(key)
        return true
      })
    }
    return {
      reach: dedup(data.recommendations.reach),
      match: dedup(data.recommendations.match),
      safety: dedup(data.recommendations.safety),
    }
  }, [data])

  // Filter items
  const filtered = useMemo(() => {
    const filter = (items: RecommendationItem[]) => {
      return items.filter(it => {
        if (filterTier && it.university.tier !== filterTier) return false
        if (filterCity && !it.university.city.includes(filterCity) && !it.university.province.includes(filterCity)) return false
        if (filterMajorCat && it.major.category !== filterMajorCat) return false
        return true
      })
    }
    if (activeTab === 'reach') return filter(allItems.reach)
    if (activeTab === 'match') return filter(allItems.match)
    return filter(allItems.safety)
  }, [allItems, activeTab, filterTier, filterCity, filterMajorCat])

  const tiers = [
    { key: 'reach' as const, label: `🔴 冲刺 (${allItems.reach.length})`, count: allItems.reach.length },
    { key: 'match' as const, label: `🟡 稳妥 (${allItems.match.length})`, count: allItems.match.length },
    { key: 'safety' as const, label: `🟢 保底 (${allItems.safety.length})`, count: allItems.safety.length },
  ]

  if (loading) {
    return (
      <div className="card">
        <div className="loading">
          <div className="spinner" />
          <p className="mt-2">正在为你智能匹配志愿方案...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="alert alert-error">{error}</div>
        <button className="btn btn-outline" onClick={() => navigate('/')}>← 返回修改信息</button>
      </div>
    )
  }

  if (!data) return null

  return (
    <div>
      <div className="steps">
        <div className="step done">① 输入分数</div>
        <div className="step done">② 兴趣测评</div>
        <div className="step active">③ 查看推荐</div>
      </div>

      {/* Student Summary Card */}
      <div className="card">
        <div className="flex-between mb-4">
          <h2>📊 志愿推荐方案</h2>
          <button className="btn btn-outline btn-sm" onClick={() => navigate('/')}>← 修改信息</button>
        </div>
        <div className="detail-grid">
          <div className="detail-stat">
            <div className="value">{data.student.score}</div>
            <div className="label">总分</div>
          </div>
          <div className="detail-stat">
            <div className="value">{data.student.province}</div>
            <div className="label">省份</div>
          </div>
          <div className="detail-stat">
            <div className="value">{data.student.category}</div>
            <div className="label">选科</div>
          </div>
          <div className="detail-stat">
            <div className="value">{data.student.estimated_rank?.toLocaleString()}</div>
            <div className="label">预估排名</div>
          </div>
          <div className="detail-stat">
            <div className="value" style={{ color: 'var(--danger)' }}>{data.summary.reach_count}</div>
            <div className="label">冲刺选项</div>
          </div>
          <div className="detail-stat">
            <div className="value" style={{ color: 'var(--warning)' }}>{data.summary.match_count}</div>
            <div className="label">稳妥选项</div>
          </div>
          <div className="detail-stat">
            <div className="value" style={{ color: 'var(--success)' }}>{data.summary.safety_count}</div>
            <div className="label">保底选项</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {tiers.map(t => (
          <button
            key={t.key}
            className={`tab ${activeTab === t.key ? 'active' : ''}`}
            onClick={() => setActiveTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="filter-bar">
        <select value={filterTier} onChange={e => setFilterTier(e.target.value)}>
          <option value="">全部层次</option>
          <option value="985">985</option>
          <option value="211">211</option>
          <option value="双一流">双一流</option>
          <option value="普通本科">普通本科</option>
        </select>
        <select value={filterMajorCat} onChange={e => setFilterMajorCat(e.target.value)}>
          <option value="">全部专业大类</option>
          {categories.map(c => (
            <option key={c.id} value={c.name}>{c.name}</option>
          ))}
        </select>
        <input
          placeholder="搜索城市..."
          value={filterCity}
          onChange={e => setFilterCity(e.target.value)}
          style={{ width: 140 }}
        />
      </div>

      {/* Recommendation List */}
      {filtered.length === 0 ? (
        <div className="empty-state">
          <p>😕 没有符合条件的推荐结果</p>
          <p className="text-muted">尝试放宽筛选条件</p>
        </div>
      ) : (
        filtered.map(item => (
          <RecCard
            key={`${item.university.id}-${item.major.id}`}
            item={item}
            onClick={() => navigate(`/detail/university/${item.university.id}`)}
          />
        ))
      )}
    </div>
  )
}

function RecCard({ item, onClick }: { item: RecommendationItem; onClick: () => void }) {
  const t = item.analysis.tier
  const tierInfo = TIER_LABELS[t] || { label: t, cls: '' }

  const compColor = item.analysis.composite_score >= 80 ? 'progress-green'
    : item.analysis.composite_score >= 60 ? 'progress-blue' : 'progress-orange'

  return (
    <div className={`rec-card tier-${t}`} onClick={onClick}>
      <div className="flex-between">
        <div>
          <span className="uni-name">{item.university.name}</span>
          <span className={`school-tier tier-${item.university.tier}`}>{item.university.tier}</span>
          <span className={`tier-badge ${tierInfo.cls}`} style={{ marginLeft: 8 }}>{tierInfo.label}</span>
        </div>
        <div className="flex-center">
          <span className="text-muted" style={{ fontSize: '.8rem' }}>综合匹配</span>
          <strong style={{ color: item.analysis.composite_score >= 80 ? 'var(--success)' : item.analysis.composite_score >= 60 ? 'var(--primary)' : 'var(--warning)' }}>
            {item.analysis.composite_score}%
          </strong>
        </div>
      </div>

      <div className="uni-meta">
        📍 {item.university.city} · {item.university.province} · {item.university.type}类
      </div>
      <div className="uni-meta">
        📚 {item.major.name} · {item.major.category} · 招收 {item.admission.enrollment_quota} 人
      </div>

      <div className="scores-row">
        <div className="score-item">最低分 <span>{item.admission.min_score}</span></div>
        <div className="score-item">平均分 <span>{item.admission.avg_score}</span></div>
        <div className="score-item">最低位次 <span>{item.admission.min_rank.toLocaleString()}</span></div>
        <div className="score-item">专业前景 <span>{item.major.prospect_score}/10</span></div>
        <div className="score-item">平均薪资 <span>¥{item.major.avg_salary.toLocaleString()}</span></div>
      </div>

      {/* Composite score breakdown */}
      <div className="mt-2" style={{ fontSize: '.78rem', color: 'var(--text-muted)' }}>
        <div className="flex-center" style={{ gap: 16 }}>
          <span>排名匹配: <strong>{item.analysis.rank_match_score}%</strong></span>
          <span>兴趣匹配: <strong>{item.analysis.interest_score}%</strong></span>
          <span>前景评分: <strong>{item.analysis.prospect_score}%</strong></span>
        </div>
        <div className="progress-bar mt-2">
          <div className={`progress-bar-fill ${compColor}`} style={{ width: `${item.analysis.composite_score}%` }} />
        </div>
      </div>
    </div>
  )
}
