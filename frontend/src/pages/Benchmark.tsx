import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Loader2, Play, Zap } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import { runBenchmark, exportModel } from '../api/detection'
import type { BenchmarkResult } from '../types'

const ENGINE_COLORS: Record<string, string> = {
  CPU: '#6b7280',
  CUDA: '#3b82f6',
  ONNX: '#10b981',
  OpenVINO: '#8b5cf6',
}

export default function Benchmark() {
  const [result, setResult] = useState<BenchmarkResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [iterations, setIterations] = useState(10)
  const [exportMsg, setExportMsg] = useState<string | null>(null)

  const handleRun = async () => {
    setLoading(true)
    try {
      const data = await runBenchmark(iterations)
      setResult(data)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const msg = await exportModel()
      setExportMsg(msg.message)
    } finally {
      setExporting(false)
    }
  }

  const chartData = result
    ? [
        { name: 'CPU', latency: result.cpu_latency_ms, fps: result.cpu_fps },
        ...(result.gpu_latency_ms != null ? [{ name: 'CUDA', latency: result.gpu_latency_ms, fps: result.gpu_fps ?? 0 }] : []),
        ...(result.onnx_latency_ms != null ? [{ name: 'ONNX', latency: result.onnx_latency_ms, fps: result.onnx_fps ?? 0 }] : []),
        ...(result.openvino_latency_ms != null ? [{ name: 'OpenVINO', latency: result.openvino_latency_ms, fps: result.openvino_fps ?? 0 }] : []),
      ]
    : []

  return (
    <div className="p-8">
      <PageHeader
        title="Benchmark"
        subtitle="Compare inference latency across CPU, CUDA GPU, ONNX Runtime, and OpenVINO"
      />

      <div className="flex items-center gap-4 mb-8">
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Iterations:</label>
          <input
            type="number"
            value={iterations}
            min={1}
            max={100}
            onChange={(e) => setIterations(Number(e.target.value))}
            className="w-20 bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
          />
        </div>
        <button
          onClick={handleRun}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-800 disabled:text-gray-600 text-white font-medium rounded-xl transition-colors"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {loading ? 'Running...' : 'Run Benchmark'}
        </button>
        <button
          onClick={handleExport}
          disabled={exporting}
          className="flex items-center gap-2 px-5 py-2 bg-purple-700 hover:bg-purple-600 disabled:bg-gray-800 text-white font-medium rounded-xl transition-colors"
        >
          {exporting ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
          Export to ONNX
        </button>
      </div>

      {exportMsg && (
        <div className="mb-6 text-sm text-green-400 bg-green-950/30 border border-green-800 rounded-lg px-4 py-3">
          {exportMsg}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'GPU Speedup', value: result.gpu_speedup, color: 'text-blue-400' },
              { label: 'ONNX Speedup', value: result.onnx_speedup, color: 'text-green-400' },
              { label: 'OpenVINO Speedup', value: result.openvino_speedup, color: 'text-purple-400' },
              { label: 'Iterations', value: result.num_iterations, color: 'text-gray-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">{label}</p>
                <p className={`text-3xl font-bold ${color}`}>
                  {value != null ? `${value}×` : '—'}
                </p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
                Latency (ms) — Lower is better
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData}>
                  <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit="ms" />
                  <Tooltip
                    contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
                    formatter={(v: number) => [`${v.toFixed(1)} ms`]}
                  />
                  <Bar dataKey="latency" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry) => (
                      <Cell key={entry.name} fill={ENGINE_COLORS[entry.name] ?? '#6b7280'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
                Throughput (FPS) — Higher is better
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData}>
                  <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} unit=" fps" />
                  <Tooltip
                    contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
                    formatter={(v: number) => [`${v.toFixed(1)} fps`]}
                  />
                  <Bar dataKey="fps" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry) => (
                      <Cell key={entry.name} fill={ENGINE_COLORS[entry.name] ?? '#6b7280'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left px-5 py-3 text-gray-500 font-medium">Engine</th>
                  <th className="text-right px-5 py-3 text-gray-500 font-medium">Latency (ms)</th>
                  <th className="text-right px-5 py-3 text-gray-500 font-medium">FPS</th>
                  <th className="text-right px-5 py-3 text-gray-500 font-medium">Speedup vs CPU</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {chartData.map((row) => (
                  <tr key={row.name} className="hover:bg-gray-800/50">
                    <td className="px-5 py-3 font-medium text-white">{row.name}</td>
                    <td className="px-5 py-3 text-right text-gray-300">{row.latency.toFixed(1)}</td>
                    <td className="px-5 py-3 text-right text-gray-300">{row.fps.toFixed(1)}</td>
                    <td className="px-5 py-3 text-right">
                      {row.name === 'CPU'
                        ? <span className="text-gray-500">baseline</span>
                        : <span className="text-blue-400 font-medium">
                            {(result.cpu_latency_ms / row.latency).toFixed(2)}×
                          </span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!result && !loading && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-16 text-center">
          <Zap className="mx-auto mb-3 text-gray-700" size={40} />
          <p className="text-gray-500">Click "Run Benchmark" to compare inference engines.</p>
        </div>
      )}
    </div>
  )
}
