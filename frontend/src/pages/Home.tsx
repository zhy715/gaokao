import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { AppState } from '../App'
import { getScoreRank } from '../api'

const PROVINCES = [
  '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
  '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
  '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州',
  '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆',
]

interface Props {
  state: AppState
  updateState: (p: Partial<AppState>) => void
}

export default function Home({ state, updateState }: Props) {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [rank, setRank] = useState<number | null>(null)
  const [error, setError] = useState('')

  const handleEstimate = async () => {
    setLoading(true)
    setError('')
    setRank(null)
    try {
      const res = await getScoreRank({
        province: state.province,
        score: state.score,
        category: state.category,
      })
      if (res.rank) setRank(res.rank)
      else setError(res.error || '查询失败')
    } catch {
      setError('无法连接后端服务，请确保后端已启动')
    } finally {
      setLoading(false)
    }
  }

  const goNext = () => navigate('/assessment')

  return (
    <div>
      {/* Steps */}
      <div className="steps">
        <div className="step active">① 输入分数</div>
        <div className="step">② 兴趣测评</div>
        <div className="step">③ 查看推荐</div>
      </div>

      <div className="card">
        <h2>📝 输入你的高考信息</h2>
        <p className="text-muted mt-2 mb-4">输入分数和省份，系统将为你智能推荐志愿方案</p>

        <div className="grid-2">
          <div className="form-group">
            <label>考生省份</label>
            <select
              value={state.province}
              onChange={e => updateState({ province: e.target.value })}
            >
              {PROVINCES.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>选科类别</label>
            <select
              value={state.category}
              onChange={e => updateState({ category: e.target.value })}
            >
              <option value="理科">理科</option>
              <option value="文科">文科</option>
              <option value="综合">综合</option>
            </select>
          </div>

          <div className="form-group">
            <label>高考总分</label>
            <input
              type="number"
              min={100}
              max={750}
              value={state.score}
              onChange={e => updateState({ score: Number(e.target.value) || 0 })}
            />
          </div>
        </div>

        <div className="flex-center mt-4" style={{ gap: 12 }}>
          <button className="btn btn-outline" onClick={handleEstimate} disabled={loading}>
            {loading ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2, marginRight: 6 }} />查询中...</> : '🔍 估算全省排名'}
          </button>
          <button className="btn btn-primary" onClick={goNext}>
            下一步：兴趣测评 →
          </button>
        </div>

        {rank !== null && (
          <div className="alert alert-success mt-4">
            🎯 你 {state.province} {state.category} 总分 {state.score} 分，
            预估全省排名约 <strong>{rank.toLocaleString()}</strong> 名
          </div>
        )}

        {error && <div className="alert alert-error mt-4">{error}</div>}
      </div>

      {/* Quick info */}
      <div className="card">
        <h2>📖 使用说明</h2>
        <div className="grid-2 mt-2">
          <div>
            <h3>🎯 冲刺</h3>
            <p className="text-muted">录取排名略低于你的排名，可以尝试报考的理想院校</p>
          </div>
          <div>
            <h3>🟡 稳妥</h3>
            <p className="text-muted">录取排名与你的排名接近，录取概率较高的院校</p>
          </div>
          <div>
            <h3>🟢 保底</h3>
            <p className="text-muted">录取排名远低于你的排名，大概率可录取的院校</p>
          </div>
          <div>
            <h3>🧠 兴趣匹配</h3>
            <p className="text-muted">完成兴趣测评，让推荐结果更符合你的个人偏好</p>
          </div>
        </div>
      </div>
    </div>
  )
}
