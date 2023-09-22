import React from 'react'

const ShowBothStations = ({result}) => {
  return (
    <div>
      <h1>Source Station name and their code</h1>
      {result.srcStation.map((station) => (
        <>
          <p>Station Name :{station.name}</p>
          <p>Station Code :{station.code}</p>
        </>
      ))}

      <h1>Destination Station name and their code</h1>
      {result.destStation.map((station) => (
        <>
          <p>Station Name :{station.name}</p>
          <p>Station Code :{station.code}</p>
        </>
      ))}
    </div>
  );
}

export default ShowBothStations
