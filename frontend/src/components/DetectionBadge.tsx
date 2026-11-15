interface Props {
  label: string
  confidence: number
}

const COLORS = [
  'bg-blue-900 text-blue-300 border-blue-700',
  'bg-green-900 text-green-300 border-green-700',
  'bg-purple-900 text-purple-300 border-purple-700',
  'bg-yellow-900 text-yellow-300 border-yellow-700',
  'bg-red-900 text-red-300 border-red-700',
  'bg-pink-900 text-pink-300 border-pink-700',
]

function colorFor(label: string): string {
  let hash = 0
  for (let i = 0; i < label.length; i++) hash = label.charCodeAt(i) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
}

export default function DetectionBadge({ label, confidence }: Props) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${colorFor(label)}`}>
      {label}
      <span className="opacity-70">{(confidence * 100).toFixed(0)}%</span>
    </span>
  )
}
