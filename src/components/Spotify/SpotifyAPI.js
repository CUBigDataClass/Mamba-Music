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

  pauseMusic = () => {
    spotifyWebApi.pause()
      .then((response) => {
        console.log(response);
      })
  }

  nextSong = () => {
  }

  prevSong = () => {
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
      <h1>
        <a href='http://localhost:3000/login'>
          <button> Login With Spotify</button>
        </a> </h1>
        <div className="f4 pa2 w-70 white center"> Now Playing: { this.state.nowPlaying.name } </div>
        <div>
          <img src={ this.state.nowPlaying.image } style={{width: 100}} />
        </div>
        <h1>
        <button onClick={() => this.getNowPlaying()}>
          Check Now Playing
        </button></h1>
        <button onClick={() => this.prevSong()}>
          Prev
        </button>        
        <button onClick={() => this.pauseMusic()}>
          Pause
        </button>
        <button onClick={() => this.nextSong()}>
          Next
        </button>
      </div>
    );
  }
}

export default SpotifyAPI;
