import React from 'react'

const ShowSingleStation = ({result}) => {
  return (
    <div>
      <h1> Station name and their code</h1>
      {result.srcStation.map((station) => (
        <>
          <p>Station Name :{station.name}</p>
          <p>Station Code :{station.code}</p>
        </>
      ))}
    </div>
  );
}

export default ShowSingleStation
