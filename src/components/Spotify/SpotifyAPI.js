import React from 'react';
import './SpotifyAPI.css';

class SpotifyAPI extends React.Component{
  constructor(props){
    super(props);
    const { getHashParams, getNowPlaying, spotifyWebApi } = this.props;
    const params = getHashParams();
    this.state={
      loggedIn: params.access_token ? true : false,
      nowPlaying: {
        name: 'Not Checked',
        image: ''
      }
    }
    if (params.access_token){
      this.spotifyWebApi.setAccessToken(params.access_token);
    }
  }
  render(){
    return(
      <div className="Spotify">
        <a href='http://localhost:3000/login'>
          <button> Login With Spotify</button>
        </a>
        <div> Now Playing: { this.state.nowPlaying.name } </div>
        <div>
          <img src={ this.state.nowPlaying.image } style={{width: 100}} />
        </div>
        <button onClick={() => this.getNowPlaying()}>
          Check Now Playing
        </button>
      </div>
    );
  }
}

export default SpotifyAPI;
