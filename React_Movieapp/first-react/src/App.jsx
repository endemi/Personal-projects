const Card = ({title}) => {
  return (
    <div className="card">
      <h2>{title}</h2>
    </div>
  )
}

const App = () => {
  return (
  <div className="card-container">
    <Card title="Star" rating={5} isCool={true}/>
    <Card title='Lion'/>
  </div>
  )
}

export default App