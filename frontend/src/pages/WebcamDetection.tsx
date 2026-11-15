import { useCallback, useEffect, useRef, useState } from 'react'
import Webcam from 'react-webcam'
import { Camera, CameraOff, Loader2 } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import DetectionBadge from '../components/DetectionBadge'
import { detectImage } from '../api/detection'
import type { DetectionResult } from '../types'

function dataURLtoFile(dataUrl: string, filename: string): File {
  const arr = dataUrl.split(',')
  const mime = arr[0].match(/:(.*?);/)![1]
  const bstr = atob(arr[1])
  const u8arr = new Uint8Array(bstr.length)
  for (let i = 0; i < bstr.length; i++) u8arr[i] = bstr.charCodeAt(i)
  return new File([u8arr], filename, { type: mime })
}

export default function WebcamDetection() {
  const webcamRef = useRef<Webcam>(null)
  const intervalRef = useRef<number | null>(null)
  const [running, setRunning] = useState(false)
  const [detections, setDetections] = useState<DetectionResult[]>([])
  const [latency, setLatency] = useState<number | null>(null)
  const [fps, setFps] = useState<number>(0)
  const [, setFrameCount] = useState(0)
  const fpsStartRef = useRef<number>(Date.now())
  const [annotatedSrc, setAnnotatedSrc] = useState<string | null>(null)

  const capture = useCallback(async () => {
    const screenshot = webcamRef.current?.getScreenshot()
    if (!screenshot) return

    try {
      const file = dataURLtoFile(screenshot, 'frame.jpg')
      const result = await detectImage(file, 'pytorch')
      setDetections(result.detections)
      setLatency(result.inference_latency_ms)
      if (result.annotated_image_base64) {
        setAnnotatedSrc(`data:image/jpeg;base64,${result.annotated_image_base64}`)
      }
      setFrameCount((c) => {
        const newCount = c + 1
        const elapsed = (Date.now() - fpsStartRef.current) / 1000
        if (elapsed >= 1) {
          setFps(Math.round(newCount / elapsed))
          fpsStartRef.current = Date.now()
          return 0
        }
        return newCount
      })
    } catch {
      // silently skip failed frames
    }
  }, [])

  useEffect(() => {
    if (running) {
      fpsStartRef.current = Date.now()
      intervalRef.current = window.setInterval(capture, 1000)
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [running, capture])

  return (
    <div className="p-8">
      <PageHeader
        title="Webcam Detection"
        subtitle="Live object detection from your webcam stream at 1 FPS"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="relative rounded-xl overflow-hidden bg-gray-900 border border-gray-800 aspect-video">
            <Webcam
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              className="w-full h-full object-cover"
              videoConstraints={{ facingMode: 'user' }}
            />
            {running && (
              <div className="absolute top-3 left-3 flex items-center gap-2">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span className="text-xs text-white font-medium bg-black/50 px-2 py-0.5 rounded">LIVE</span>
              </div>
            )}
            {latency !== null && (
              <div className="absolute top-3 right-3 text-xs text-white bg-black/60 px-2 py-1 rounded">
                {latency.toFixed(0)} ms · {fps} FPS
              </div>
            )}
          </div>

          <button
            onClick={() => setRunning((r) => !r)}
            className={`w-full py-3 font-medium rounded-xl transition-colors flex items-center justify-center gap-2 ${
              running
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {running ? <><CameraOff size={17} /> Stop Detection</> : <><Camera size={17} /> Start Detection</>}
          </button>
        </div>

        <div className="space-y-4">
          {annotatedSrc && (
            <div className="rounded-xl overflow-hidden bg-gray-900 border border-gray-800">
              <img src={annotatedSrc} alt="Annotated frame" className="w-full" />
            </div>
          )}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">
              Live Detections
              {running && <Loader2 size={13} className="inline ml-2 animate-spin text-blue-400" />}
            </h3>
            {detections.length === 0 ? (
              <p className="text-gray-600 text-sm">
                {running ? 'Waiting for detections...' : 'Start detection to see results.'}
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {detections.map((d, i) => (
                  <DetectionBadge key={i} label={d.class} confidence={d.confidence} />
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Objects', value: detections.length },
              { label: 'Latency', value: latency != null ? `${latency.toFixed(0)}ms` : '—' },
              { label: 'FPS', value: running ? fps : '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-center">
                <p className="text-xs text-gray-500">{label}</p>
                <p className="text-lg font-bold text-blue-400">{value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
