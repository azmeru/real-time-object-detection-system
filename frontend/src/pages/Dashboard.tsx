import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Activity, Target, Cpu, Zap } from 'lucide-react'
import StatCard from '../components/StatCard'
import PageHeader from '../components/PageHeader'
import { getStats, getDeviceInfo } from '../api/detection'
import type { DetectionStats, DeviceInfo } from '../types'

export default function Dashboard() {
  const [stats, setStats] = useState<DetectionStats | null>(null)
  const [device, setDevice] = useState<DeviceInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getStats(), getDeviceInfo()])
      .then(([s, d]) => { setStats(s); setDevice(d) })
      .finally(() => setLoading(false))
  }, [])

  const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']

  return (
    <div className="p-8">
      <PageHeader
        title="Dashboard"
        subtitle="Real-time overview of your object detection platform"
      />

      {loading ? (
        <div className="text-gray-500">Loading...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard
              title="Total Detections"
              value={stats?.total_detections ?? 0}
              icon={<Target size={18} />}
              accent="blue"
            />
            <StatCard
              title="Avg Confidence"
              value={stats ? `${(stats.average_confidence * 100).toFixed(1)}%` : '—'}
              icon={<Activity size={18} />}
              accent="green"
            />
            <StatCard
              title="Inference Device"
              value={device?.device.toUpperCase() ?? '—'}
              subtitle={device?.gpu_name ?? undefined}
              icon={<Cpu size={18} />}
              accent="purple"
            />
            <StatCard
              title="CUDA Available"
              value={device?.cuda_available ? 'Yes' : 'No'}
              subtitle={device?.cuda_version ? `v${device.cuda_version}` : undefined}
              icon={<Zap size={18} />}
              accent={device?.cuda_available ? 'yellow' : 'blue'}
            />
          </div>

          {stats && stats.top_classes.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
                Top Detected Classes
              </h2>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={stats.top_classes} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <XAxis dataKey="class" stroke="#6b7280" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
                    labelStyle={{ color: '#f9fafb' }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {stats.top_classes.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {stats?.total_detections === 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
              <Target className="mx-auto mb-3 text-gray-700" size={40} />
              <p className="text-gray-500">No detections yet. Upload an image to get started.</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
