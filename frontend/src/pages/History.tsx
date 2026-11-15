import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight, Clock } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import { getDetections } from '../api/detection'
import type { PaginatedDetections } from '../types'

export default function History() {
  const [data, setData] = useState<PaginatedDetections | null>(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getDetections(page, 20)
      .then(setData)
      .finally(() => setLoading(false))
  }, [page])

  const deviceColor = (d: string) => {
    if (d.includes('cuda')) return 'text-blue-400'
    if (d.includes('onnx')) return 'text-green-400'
    if (d.includes('openvino')) return 'text-purple-400'
    return 'text-gray-400'
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Detection History"
        subtitle="All stored detection records from the database"
      />

      {loading ? (
        <div className="text-gray-500">Loading...</div>
      ) : !data || data.total === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-16 text-center">
          <Clock className="mx-auto mb-3 text-gray-700" size={40} />
          <p className="text-gray-500">No detection records yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-gray-500">{data.total} total records</p>
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-left">
                  <th className="px-5 py-3 text-gray-500 font-medium">ID</th>
                  <th className="px-5 py-3 text-gray-500 font-medium">File</th>
                  <th className="px-5 py-3 text-gray-500 font-medium">Class</th>
                  <th className="px-5 py-3 text-gray-500 font-medium">Confidence</th>
                  <th className="px-5 py-3 text-gray-500 font-medium">Device</th>
                  <th className="px-5 py-3 text-gray-500 font-medium">Latency</th>
                  <th className="px-5 py-3 text-gray-500 font-medium">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {data.items.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-800/50">
                    <td className="px-5 py-3 text-gray-500">#{r.id}</td>
                    <td className="px-5 py-3 text-gray-300 max-w-32 truncate">{r.filename}</td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-0.5 bg-blue-950 text-blue-300 border border-blue-800 rounded-full text-xs">
                        {r.detected_class}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-gray-300">{(r.confidence * 100).toFixed(1)}%</td>
                    <td className={`px-5 py-3 font-medium ${deviceColor(r.inference_device)}`}>
                      {r.inference_device}
                    </td>
                    <td className="px-5 py-3 text-gray-300">
                      {r.inference_latency_ms != null ? `${r.inference_latency_ms.toFixed(1)} ms` : '—'}
                    </td>
                    <td className="px-5 py-3 text-gray-500 text-xs">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-gray-300"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-sm text-gray-400">
                Page {page} of {data.total_pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                disabled={page === data.total_pages}
                className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-gray-300"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
