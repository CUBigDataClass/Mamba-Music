import React from 'react';
import Tilt from 'react-tilt';
import MusicLogo from './MusicLogo.png'
import './Logo.css';

const Logo = () => {
  return (
    <div className='ma4 mt0'>
      <Tilt className="Tilt br2 shadow-2" options={{ max : 55 }} style={{ height: 150, width: 150, display: 'flex'}} >
        <div className="Tilt-inner pa3">
          <img style={{paddingTop: '5px', height: '100px', width: 'auto'}} alt='logo' src={MusicLogo}/>
        </div>
      </Tilt>
    </div>
  );
}

export default Logo;
