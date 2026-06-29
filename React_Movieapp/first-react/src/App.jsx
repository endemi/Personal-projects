import { useEffect, useState } from 'react'
import Search from './components/Search'

const API_BASE_URL = 'https://api.themoviedb.org/3'

const API_KEY = import.meta.env.VITE_TMDB_API_KEY

const API_OPTIONS = {
    method: 'GET',
    headers: {
        accept: 'application/json',
        Authorization: `Bearer ${API_KEY}`
    }
}

const App = () => {
    const [searchTerm, setsearchTerm] = useState('');

    const [errorMessage, seterrorMessage] = useState('');

    const fetchMovies = async () => {
        try {
          const endpoint = `${API_BASE_URL}/discover/movie?sort_by=popularity.desc`;
          const response = await fetch(endpoint, API_OPTIONS);
          const [movieList, setmovieList] = useState([])
          const [isLoading, setisLoading] = useState(False)

          if(!response.ok) {
            throw new Error('Failed to fetch movies');
          }
          
          const data = await response.json();

          if(data.Response == 'False') {
            seterrorMessage(data.Error || 'Failed to fetch movies');
          }
        } catch (error) {
            console.error(`Error fetching movies: ${error}`);
            seterrorMessage('Error fetching movies. Please try again later.');
        }
    }

    useEffect(() => {
        fetchMovies();
    }, []);

  return (
    <main>
        
        <div className='pattern'/>

        <div className='wrapper'>
            <header>
                <img src="./hero.png" alt='Hero Banner'/>
                <h1>Find <span className='text-gradient'>Movies</span> You'll Enjoy Without the Hassle</h1>

                <Search searchTerm={searchTerm} setsearchTerm={setsearchTerm} />
            </header>

            <section className='all-movies'>
                <h2>All Movies</h2>

                {errorMessage && <p className='text-red-500'>{errorMessage}</p>}
            </section>

        </div>
    </main>
  )
}

export default App
