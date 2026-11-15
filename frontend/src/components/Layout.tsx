import { NavLink, Outlet } from 'react-router-dom'
import { Activity, Camera, Image, BarChart2, Clock, Cpu } from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/', label: 'Dashboard', icon: Activity, end: true },
  { to: '/detect', label: 'Image Detection', icon: Image },
  { to: '/webcam', label: 'Webcam', icon: Camera },
  { to: '/benchmark', label: 'Benchmark', icon: BarChart2 },
  { to: '/history', label: 'History', icon: Clock },
]

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950">
      <aside className="w-60 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-5 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Cpu className="text-blue-500" size={22} />
            <span className="font-bold text-white text-sm leading-tight">
              Object Detection<br />
              <span className="text-blue-400 font-normal">Platform</span>
            </span>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                )
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-800 text-xs text-gray-600">
          YOLOv8 · CUDA · ONNX · OpenVINO
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
