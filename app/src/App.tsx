import { Route, Routes } from 'react-router-dom'
import { Calendar } from '@/pages/Calendar'
import { Diagnostic } from '@/pages/Diagnostic'
import { Drill } from '@/pages/Drill'
import { Lesson } from '@/pages/Lesson'
import { MistakeNotebook } from '@/pages/MistakeNotebook'
import { MockAnalysis } from '@/pages/MockAnalysis'
import { MockPlayer } from '@/pages/MockPlayer'
import { PassageSetPlayer } from '@/pages/PassageSetPlayer'
import { Review } from '@/pages/Review'
import { Settings } from '@/pages/Settings'
import { Today } from '@/pages/Today'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Today />} />
      <Route path="/diagnostic" element={<Diagnostic />} />
      <Route path="/calendar" element={<Calendar />} />
      <Route path="/lesson/:topicId" element={<Lesson />} />
      <Route path="/drill/:topicId" element={<Drill />} />
      <Route path="/set/:setId" element={<PassageSetPlayer />} />
      <Route path="/mock/:mockId" element={<MockPlayer />} />
      <Route path="/mock-result/:resultId" element={<MockAnalysis />} />
      <Route path="/mistakes" element={<MistakeNotebook />} />
      <Route path="/review" element={<Review />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  )
}

export default App
