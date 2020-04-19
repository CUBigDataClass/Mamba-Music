import React from 'react';
import './SpotifyAPI.css';
import Spotify from 'spotify-web-api-js';

const spotifyWebApi = new Spotify();

class SpotifyAPI extends React.Component{
  getHashParams = () => {
    var hashParams = {};
    var e, r = /([^&;=]+)=?([^&;]*)/g,
        q = window.location.hash.substring(1);
    while ( e = r.exec(q)) {
       hashParams[e[1]] = decodeURIComponent(e[2]);
    }
    return hashParams;
  }

  getNowPlaying = () => {
    spotifyWebApi.getMyCurrentPlaybackState()
      .then((response) => {
        this.setState({
          nowPlaying: {
            name: response.item.name,
            image: response.item.album.images[0].url
          }
        })
      })
  }

  constructor(props){
    super(props);
    // const { getHashParams, getNowPlaying, spotifyWebApi } = this.props;
    const params = this.getHashParams();
    this.state={
      loggedIn: params.access_token ? true : false,
      nowPlaying: {
        name: 'Not Checked',
        image: ''
      }
    }
    if (params.access_token){
      console.log(params.access_token)
      console.log(params.refresh_token)
      spotifyWebApi.setAccessToken(params.access_token);
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
