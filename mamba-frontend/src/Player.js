import React from "react";
import Play from './Buttons/Play';
import Pause from './Buttons/Pause';
import Previous from './Buttons/Previous';
import Next from './Buttons/Next';
import Like from './Buttons/Like';
import Dislike from './Buttons/Dislike';

import "./Player.css";

import { Modal, Button } from 'react-bootstrap';
import axios from 'axios';
import defaultMusicJson from './defaultMusicJson';

class Player extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      musicInfo: defaultMusicJson,
      playing: false,
      currentIndex: 0,
      userLikeMusic: null,
      userDislikeMusic: null,
      userGoogleId: null
    };
  }

  foo() {
    window.setInterval(() => {
      var audio = document.getElementById('myAudio');
      if (audio.ended === true) {
        this.onNextClick()
      } 
    }, 100)
  }

  componentDidMount() {
    this.updateMusicInfo()
  }

  updateMusicInfo() {
    this.props.musicInfo(this.state.musicInfo)
    this.props.currentMusic(this.state.currentIndex)
  }

  onComponentUpdate() {
    this.updateMusicInfo()
    this.onPrevOrNextClick()
  }

  componentDidUpdate(prevProps) {
    if(prevProps.changeRadio !== this.props.changeRadio) {
      let callArtist
      switch(this.props.changeRadio) {
        case 0:
          callArtist = 'melody_rnn'
          break;
        case 1:
          callArtist = 'performance_rnn';
          break;
        case 2:
          callArtist = 'polyphony_rnn';
          break;
        case 3:
          callArtist = 'pianoroll_rnn_nade';
          break;
        case 4:
          callArtist = 'improv_rnn';
          break;
        case 5:
          callArtist = 'music_vae';
          break;
        case 6:
          callArtist = 'music_transformer';
          break;
        default:
          callArtist = null
      }

      const querystring = require('querystring');
        let userId = this.state.userGoogleId
        let getLink = 'https://7xetws0aoh.execute-api.us-west-1.amazonaws.com/Prod/Queue?' + querystring.stringify({ CustomerId: userId }) + '&' + querystring.stringify({ artist: callArtist })

        axios.get(getLink)
        .then((responseGet) => {
          this.setState({ musicInfo: responseGet.data.ids, currentIndex: 0 }, this.onComponentUpdate)
      })
    }
    if(prevProps.isUserLoggedIn !== this.props.isUserLoggedIn) {
      const querystring = require('querystring');
      let userId = this.state.userGoogleId
      let getLink = 'https://7xetws0aoh.execute-api.us-west-1.amazonaws.com/Prod/Queue?' + querystring.stringify({ CustomerId: userId }) + '&' + querystring.stringify({ artist: 'music_transformer' })

      axios.get(getLink)
      .then((responseGet) => {
        this.setState({ musicInfo: responseGet.data.ids, currentIndex: 0 }, this.updateMusicInfo)
      })

      this.checkLikedDisliked()
    }
  }

  onPreviousClick = () => {
    if(this.props.isUserLoggedIn) {
      if(this.state.currentIndex > 0){
        this.setState({ currentIndex: this.state.currentIndex - 1}, this.onPrevOrNextClick)
      } else {
        this.setState({ currentIndex: 0})
      }
    } else {
      this.setState({ showModal: true })
    }
  }

  onNextClick = () => {
    if(this.props.isUserLoggedIn) {
      if(this.state.currentIndex < this.state.musicInfo.length - 1){
        this.setState({ currentIndex: this.state.currentIndex + 1}, this.onPrevOrNextClick)
      } else {
        const querystring = require('querystring');
        let userId = this.state.userGoogleId
        let getLink = 'https://7xetws0aoh.execute-api.us-west-1.amazonaws.com/Prod/Queue?' + querystring.stringify({ CustomerId: userId }) + '&' + querystring.stringify({ artist: 'music_transformer' })

        axios.get(getLink)
        .then((responseGet) => {
          this.setState({ musicInfo: responseGet.data.ids, currentIndex: 0 }, this.updateMusicInfo)
        })
      }
    } else {
      this.setState({ showModal: true })
    }
  }

  onPrevOrNextClick = () => {
    this.playPauseAudio();
    this.checkLikedDisliked()
  }

  checkLikedDisliked() {
    const querystring = require('querystring');
    let getUser = this.props.userInfo.googleId
    let getUserInfoLink = 'https://q2nypxvh02.execute-api.us-west-1.amazonaws.com/Prod/Users?'+ querystring.stringify({ CustomerId: getUser })
    
    axios.get(getUserInfoLink)
    .then((responseGet) => {
        if(responseGet.data.hasOwnProperty("Item")){
            let likeMusic = responseGet.data.Item.likes 
            let dislikeMusic = responseGet.data.Item.dislikes 
            if(likeMusic) {
              if(likeMusic.includes(this.state.musicInfo[this.state.currentIndex].SongId)) {
                this.setState({ userLikeMusic: true, userDislikeMusic: false })
              }
            }
            if(dislikeMusic) {
              if(dislikeMusic.includes(this.state.musicInfo[this.state.currentIndex].SongId)) {
                this.setState({ userLikeMusic: false, userDislikeMusic: true })
              }
            }

            if(likeMusic && dislikeMusic) {
              if(!likeMusic.includes(this.state.musicInfo[this.state.currentIndex].SongId) && !dislikeMusic.includes(this.state.musicInfo[this.state.currentIndex].SongId)) {
                this.setState({ userLikeMusic: false, userDislikeMusic: false })
              }
            }
        } else {
          this.setState({ userLikeMusic: false, userDislikeMusic: false })
        }
    });
  }

  onDislikeClick = () => {
    if(this.props.isUserLoggedIn) {
      this.setState({ userLikeMusic: false, userDislikeMusic: true })
      axios({
        method: 'put',
        url: 'https://q2nypxvh02.execute-api.us-west-1.amazonaws.com/Prod/Users',
        data: {
          CustomerId: this.props.userInfo.googleId,
          dislikes: this.state.musicInfo[this.state.currentIndex].SongId
        }
      })
    } else {
      this.setState({ showModal: true })
    }
  }

  onLikeClick = () => {
    if(this.props.isUserLoggedIn) {
      this.setState({ userLikeMusic: true, userDislikeMusic: false })
      axios({
        method: 'put',
        url: 'https://q2nypxvh02.execute-api.us-west-1.amazonaws.com/Prod/Users',
        data: {
          CustomerId: this.props.userInfo.googleId,
          likes: this.state.musicInfo[this.state.currentIndex].SongId
        }
      })
    } else {
      this.setState({ showModal: true })
    }
  }

  togglePlayPause = () => {
    if(this.props.isUserLoggedIn) {
      this.setState({ playing: !this.state.playing }, this.playPauseAudio)
    } else {
      this.setState({ showModal: true })
    }
  }

  playPauseAudio = () => {
    this.props.currentMusic(this.state.currentIndex)
    let track = "https://storage.googleapis.com/mamba_songs_bucket/"+this.state.musicInfo[this.state.currentIndex].SongId+".mp3" 
    if(this.state.playing) {
      this.player.src = track 
      this.player.play() 
    } else {
      this.player.pause()
    }
    this.foo()
  }

  render() {
    return (
      <footer className="footer">
        <div className="player" >
          {
            this.state.showModal && (
              <Modal show={this.state.showModal} aria-labelledby="contained-modal-title-vcenter" centered>
                <Modal.Header>
                  <Modal.Title>User Not Logged In!</Modal.Title>
                </Modal.Header>
                <Modal.Body>Please login to use this feature!</Modal.Body>
                <Modal.Footer>
                  <Button variant="primary" onClick={() => this.setState({ showModal: false })}>
                    OK
                  </Button>
                </Modal.Footer>
              </Modal>
            )
          }

          <audio ref={ref => (this.player = ref)} id="myAudio" preload="metadata"/>
          {this.state.userDislikeMusic ? (<Dislike onDislikeClick={this.onDislikeClick} ButtonOpacity={1}/>) : (<Dislike onDislikeClick={this.onDislikeClick} ButtonOpacity={0.25}/>)}
          <Previous onPreviousClick={this.onPreviousClick}/>
          {this.state.playing ? <Pause onPlayerClick={this.togglePlayPause} /> : <Play onPlayerClick={this.togglePlayPause}/>}
          <Next onNextClick={this.onNextClick}/>
          {this.state.userLikeMusic ? (<Like onLikeClick={this.onLikeClick} ButtonOpacity={1}/>) : (<Like onLikeClick={this.onLikeClick} ButtonOpacity={0.25}/>)}
        </div>
      </footer>
    );
  }
}

export default Player;