import React from 'react';

const Rank = ({name, entries}) => {
  return (
    <div>
      <div className='white f3'>
        {`${name} Songs Downloaded: ${entries}` }
      </div>
    </div>
  );
}

export default Rank;
