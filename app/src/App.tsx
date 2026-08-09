import { Route, Routes } from 'react-router-dom'
import { Drill } from '@/pages/Drill'
import { Today } from '@/pages/Today'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Today />} />
      <Route path="/drill/:topicId" element={<Drill />} />
    </Routes>
  )
}

export default App
