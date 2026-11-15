import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Loader2, AlertCircle } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import DetectionBadge from '../components/DetectionBadge'
import { detectImage, type InferenceBackend } from '../api/detection'
import type { DetectionResponse } from '../types'

const BACKENDS: { value: InferenceBackend; label: string }[] = [
  { value: 'pytorch', label: 'PyTorch (YOLO)' },
  { value: 'onnx', label: 'ONNX Runtime' },
  { value: 'openvino', label: 'OpenVINO' },
]

export default function ImageDetection() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<DetectionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [backend, setBackend] = useState<InferenceBackend>('pytorch')

  const onDrop = useCallback((accepted: File[]) => {
    const f = accepted[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.bmp'] },
    maxFiles: 1,
  })

  const handleDetect = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const data = await detectImage(file, backend)
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Detection failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Image Detection"
        subtitle="Upload an image and detect objects using YOLOv8"
      />

      <div className="flex gap-2 mb-6">
        {BACKENDS.map((b) => (
          <button
            key={b.value}
            onClick={() => setBackend(b.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              backend === b.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {b.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-blue-500 bg-blue-950/30' : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto mb-3 text-gray-600" size={36} />
            <p className="text-gray-400 text-sm">
              {isDragActive ? 'Drop the image here...' : 'Drag & drop an image, or click to browse'}
            </p>
            <p className="text-gray-600 text-xs mt-1">JPG, PNG, WEBP, BMP</p>
          </div>

          {preview && (
            <div className="rounded-xl overflow-hidden bg-gray-900 border border-gray-800">
              <img src={preview} alt="Preview" className="w-full object-contain max-h-64" />
            </div>
          )}

          <button
            onClick={handleDetect}
            disabled={!file || loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-800 disabled:text-gray-600 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            {loading ? <><Loader2 size={17} className="animate-spin" /> Detecting...</> : 'Run Detection'}
          </button>

          {error && (
            <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900 rounded-lg px-4 py-3 text-sm">
              <AlertCircle size={16} /> {error}
            </div>
          )}
        </div>

        <div>
          {result ? (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-white">Results</h3>
                <span className="text-xs text-gray-500">
                  {result.inference_latency_ms.toFixed(1)} ms · {result.inference_device}
                </span>
              </div>

              {result.annotated_image_base64 && (
                <img
                  src={`data:image/jpeg;base64,${result.annotated_image_base64}`}
                  alt="Annotated"
                  className="w-full rounded-lg"
                />
              )}

              <div>
                <p className="text-xs text-gray-500 mb-2">
                  {result.detections.length} object{result.detections.length !== 1 ? 's' : ''} detected
                </p>
                <div className="flex flex-wrap gap-2">
                  {result.detections.length === 0 ? (
                    <p className="text-gray-600 text-sm">No objects detected above confidence threshold.</p>
                  ) : (
                    result.detections.map((d, i) => (
                      <DetectionBadge key={i} label={d.class} confidence={d.confidence} />
                    ))
                  )}
                </div>
              </div>

              <div className="border-t border-gray-800 pt-3 grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-gray-500">Backend</span>
                  <p className="text-white font-medium">{result.inference_device}</p>
                </div>
                <div>
                  <span className="text-gray-500">Latency</span>
                  <p className="text-white font-medium">{result.inference_latency_ms.toFixed(2)} ms</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-10 text-center text-gray-600">
              Upload an image and click Run Detection to see results here.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
