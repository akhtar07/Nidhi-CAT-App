import { Route, Routes } from 'react-router-dom'
import { Drill } from '@/pages/Drill'
import { Lesson } from '@/pages/Lesson'
import { Settings } from '@/pages/Settings'
import { Today } from '@/pages/Today'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Today />} />
      <Route path="/lesson/:topicId" element={<Lesson />} />
      <Route path="/drill/:topicId" element={<Drill />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  )
}

export default App
