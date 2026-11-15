import api from './client'
import type {
  DetectionResponse,
  PaginatedDetections,
  BenchmarkResult,
  DeviceInfo,
  DetectionStats,
} from '../types'

export type InferenceBackend = 'pytorch' | 'onnx' | 'openvino'

const ENDPOINT: Record<InferenceBackend, string> = {
  pytorch: '/detect/',
  onnx: '/detect/onnx',
  openvino: '/detect/openvino',
}

export async function detectImage(
  file: File,
  backend: InferenceBackend = 'pytorch'
): Promise<DetectionResponse> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<DetectionResponse>(ENDPOINT[backend], form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getDetections(page = 1, pageSize = 20): Promise<PaginatedDetections> {
  const { data } = await api.get<PaginatedDetections>('/detections/', {
    params: { page, page_size: pageSize },
  })
  return data
}

export async function getStats(): Promise<DetectionStats> {
  const { data } = await api.get<DetectionStats>('/detections/stats')
  return data
}

export async function runBenchmark(iterations = 10): Promise<BenchmarkResult> {
  const { data } = await api.get<BenchmarkResult>('/benchmark/', {
    params: { iterations },
  })
  return data
}

export async function getDeviceInfo(): Promise<DeviceInfo> {
  const { data } = await api.get<DeviceInfo>('/system/device')
  return data
}

export async function exportModel(): Promise<{ message: string }> {
  const { data } = await api.post<{ message: string }>('/models/export')
  return data
}
