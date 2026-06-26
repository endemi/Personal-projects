const Card = ({title}) => {
  return (
    <h2>{title}</h2>
  )
}

const App = () => {
  return (
  <div>
    <h2>Functional </h2>
    <Card title="Star" rating={5} isCool={true} actors={[{name:'Actors'}]}/>
    <Card title='Lion'/>
  </div>
  )
}

export default App