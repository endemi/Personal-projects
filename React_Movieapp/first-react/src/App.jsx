import { useEffect, useState } from 'react'
import Search from './components/Search'

const API_BASE_URL = 'https://api.themoviedb.org/3'

const API_KEY = import.meta.env.VITE_TMDB_API_KEY

const App = () => {
    const [searchTerm, setsearchTerm] = useState('');
    const [errorMessage, seterrorMessage] = useState('');
    const [movieList, setmovieList] = useState([]);
    const [isLoading, setisLoading] = useState(false);

    const fetchMovies = async () => {
        setisLoading(true);
        seterrorMessage('');

        try {
          const endpoint = `${API_BASE_URL}/discover/movie?sort_by=popularity.desc&api_key=${API_KEY}`;
          const response = await fetch(endpoint);

          if(!response.ok) {
            throw new Error('Failed to fetch movies');
          }
          
          const data = await response.json();

          if(data.status_message) {
            seterrorMessage(data.status_message || 'Failed to fetch movies');
            setmovieList([]);
            return;
          }
          
          setmovieList(data.results || []);
        } catch (error) {
            console.error(`Error fetching movies: ${error}`);
            seterrorMessage('Error fetching movies. Please try again later.');
        } finally {
            setisLoading(false);
        }
    };

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

                {isLoading ? (
                    <p>Loading...</p>
                ) : errorMessage ? (
                    <p className='text-red-500'>{errorMessage}</p>
                ) : (
                    <ul>
                        {movieList.map((movie) => (
                            <li key={movie.id} className='text-white'>
                                {movie.title}
                            </li>
                        ))}
                    </ul>
                )}
            </section>

        </div>
    </main>
  )
}

export default App