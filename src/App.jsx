import { useState } from 'react'
import axios from 'axios'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResponse('')
    try {
      // Memanggil fungsi Python di Vercel
      const res = await axios.post('/api/chat', { query })
      setResponse(res.data.answer)
    } catch (error) {
      setResponse("Maaf, terjadi kesalahan saat menghubungi server.")
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col items-center justify-center p-6 font-serif">
      <div className="w-full max-w-2xl bg-[#F4EFE6] rounded-xl shadow-sm border border-[#E8DFD1] p-8">
        <h1 className="text-3xl text-[#5C4D3C] font-bold mb-2 text-center">Smart Assistant</h1>
        <p className="text-[#8B7B6B] text-center mb-8">Tanyakan apa saja berdasarkan data yang kita miliki.</p>
        
        <form onSubmit={handleSearch} className="flex gap-3 mb-6">
          <input
            type="text"
            className="flex-1 px-4 py-3 rounded-lg border border-[#D5C7B5] bg-white text-[#4A3F33] focus:outline-none focus:border-[#967E62]"
            placeholder="Tulis pertanyaanmu di sini..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button 
            type="submit" 
            disabled={loading}
            className="px-6 py-3 bg-[#8C6B4A] hover:bg-[#73573A] text-white rounded-lg font-medium transition-colors"
          >
            {loading ? 'Mencari...' : 'Tanya'}
          </button>
        </form>

        {response && (
          <div className="bg-white p-6 rounded-lg border border-[#D5C7B5] text-[#5C4D3C] leading-relaxed">
            {response}
          </div>
        )}
      </div>
    </div>
  )
}

export default App