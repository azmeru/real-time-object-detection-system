export interface DetectionResult {
  class: string
  confidence: number
  bbox: [number, number, number, number]
}

export interface DetectionResponse {
  filename: string
  detections: DetectionResult[]
  inference_device: string
  inference_latency_ms: number
  annotated_image_base64?: string
}

export interface DetectionRecord {
  id: number
  filename: string
  detected_class: string
  confidence: number
  bbox_x1: number
  bbox_y1: number
  bbox_x2: number
  bbox_y2: number
  inference_device: string
  inference_latency_ms: number | null
  created_at: string
}

export interface PaginatedDetections {
  items: DetectionRecord[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface BenchmarkResult {
  cpu_latency_ms: number
  cpu_fps: number
  gpu_latency_ms: number | null
  gpu_fps: number | null
  onnx_latency_ms: number | null
  onnx_fps: number | null
  openvino_latency_ms: number | null
  openvino_fps: number | null
  gpu_speedup: number | null
  onnx_speedup: number | null
  openvino_speedup: number | null
  num_iterations: number
}

export interface DeviceInfo {
  device: string
  gpu_name: string | null
  cuda_available: boolean
  cuda_version: string | null
  openvino_available: boolean
}

export interface DetectionStats {
  total_detections: number
  average_confidence: number
  top_classes: { class: string; count: number }[]
}
