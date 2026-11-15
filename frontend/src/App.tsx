import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ImageDetection from './pages/ImageDetection'
import WebcamDetection from './pages/WebcamDetection'
import Benchmark from './pages/Benchmark'
import History from './pages/History'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="detect" element={<ImageDetection />} />
          <Route path="webcam" element={<WebcamDetection />} />
          <Route path="benchmark" element={<Benchmark />} />
          <Route path="history" element={<History />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
