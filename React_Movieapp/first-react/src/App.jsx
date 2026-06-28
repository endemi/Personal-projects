import { useState } from "react"

const Card = ({title}) => {
  const [hasLiked, setHasLiked] = useState(false);

  return (
    <div className="card">
      <h2>{title}</h2>

      <button onClick={() => setHasLiked(!hasLiked)}>
        {hasLiked ? '❤️' : '💛'}
      </button>

    </div>
  )
}

const App = () => {
  const [hasLiked, setHasLiked] = useState(false);


  return (
  <div className="card-container">
    <Card title="Star" rating={5} isCool={true}/>
    <Card title='Lion'/>
  </div>
  )
}

export default App