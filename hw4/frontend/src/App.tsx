import { Outlet } from 'react-router-dom'
import NavBar from './components/NavBar'
import ChatPanel from './components/ChatPanel'
import HandsomeDan from './components/HandsomeDan'

export default function App() {
  return (
    <>
      <NavBar />
      <main>
        <Outlet />
      </main>
      <footer className="footer">
        <div className="footer-inner">
          <HandsomeDan size={30} />
          <span>Campus Customs · 57 Broadway, New Haven, CT · Officially licensed Yale apparel</span>
        </div>
      </footer>
      <ChatPanel />
    </>
  )
}
