import { Route, Routes } from 'react-router-dom'
import { Drill } from '@/pages/Drill'
import { Lesson } from '@/pages/Lesson'
import { PassageSetPlayer } from '@/pages/PassageSetPlayer'
import { Settings } from '@/pages/Settings'
import { Today } from '@/pages/Today'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Today />} />
      <Route path="/lesson/:topicId" element={<Lesson />} />
      <Route path="/drill/:topicId" element={<Drill />} />
      <Route path="/set/:setId" element={<PassageSetPlayer />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  )
}

export default App
