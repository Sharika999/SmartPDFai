import './App.css'
import { Header } from './components/Header';
import { ChatBox } from './components/ChatBox';
import KeepAlive from './components/KeepAlive';

function App() {
  return (
    <div className="App flex flex-col min-h-screen items-center">
      <KeepAlive />
      <Header />
      <ChatBox />
      <p className='text-sm mt-2 text-gray-500'>
  Built by Sharika 🚀
</p>

      <p className='text-sm mt-2 text-gray-500'>
        Made by <a href="https://jaimingodhani.me" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">Jaimin Godhani</a>
      </p>
    </div>
  );
}

export default App
