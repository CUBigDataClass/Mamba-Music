import React from 'react';
import './ImageLinkForm.css'

const ImageLinkForm = ({ onInputChange, onButtonSubmit }) => {
  return (
    <div>
      <p className='f3' style={{color: "white"}}>
        {'Upload an image URL below:'}
      </p>
      <div className='center'>
        <div className='form center pa4 br3 shadow-5'>
          <input className='f4 pa2 w-70 center' type='tex' onChange={onInputChange}/>
          <button
          className='w-30 grow f4 link ph3 pv2 dib white bg-dark-blue'
          onClick={onButtonSubmit}
          >Upload Song</button>
        </div>
      </div>
    </div>
  );
}

export default ImageLinkForm;
