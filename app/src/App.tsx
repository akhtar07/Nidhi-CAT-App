import { Route, Routes } from 'react-router-dom'
import { BottomNav } from '@/components/AppShell'
import { Bookmarks } from '@/pages/Bookmarks'
import { Calendar } from '@/pages/Calendar'
import { Diagnostic } from '@/pages/Diagnostic'
import { Drill } from '@/pages/Drill'
import { Lesson } from '@/pages/Lesson'
import { MistakeNotebook } from '@/pages/MistakeNotebook'
import { MockAnalysis } from '@/pages/MockAnalysis'
import { MockPlayer } from '@/pages/MockPlayer'
import { PassageSetPlayer } from '@/pages/PassageSetPlayer'
import { Progress } from '@/pages/Progress'
import { Review } from '@/pages/Review'
import { Settings } from '@/pages/Settings'
import { Today } from '@/pages/Today'
import { UpdateBanner } from '@/pwa/UpdateBanner'
import { useAutoSync } from '@/storage/supabase/useAutoSync'

function App() {
  useAutoSync()
  return (
    <>
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
        <Route path="/bookmarks" element={<Bookmarks />} />
        <Route path="/progress" element={<Progress />} />
        <Route path="/review" element={<Review />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
      <BottomNav />
      <UpdateBanner />
    </>
  )
}

export default App
