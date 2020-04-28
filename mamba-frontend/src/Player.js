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
import SongsJson from "./SongsJson"
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

  componentDidMount() {
    this.updateMusicInfo()
  }

  // TODO: need to call this on every server call to music, and on every server call to music, update these states
  updateMusicInfo() {
    this.props.musicInfo(this.state.musicInfo)
    this.props.currentMusic(this.state.currentIndex)
  }

  componentDidUpdate(prevProps) {
    if(prevProps.changeRadio !== this.props.changeRadio) {
      console.log("NEW Radio Selected: ", this.props.changeRadio)

      // TODO: make a call here to update the musicInfo for new SongsJson
      this.setState({ musicInfo: SongsJson, currentIndex: 0 }, this.updateMusicInfo)
    }
    if(prevProps.isUserLoggedIn !== this.props.isUserLoggedIn) {
      // TODO: call the queue api here with the first radio artist to get the music the very first time
      this.setState({ musicInfo: SongsJson, currentIndex: 0 }, this.updateMusicInfo)

      let getUser = this.props.userInfo.googleId
      console.log(getUser)
      if(getUser) {
        this.setState({ userGoogleId: getUser.toString() })
        let likeMusic = this.state.musicInfo[this.state.currentIndex].likes 
        let dislikeMusic = this.state.musicInfo[this.state.currentIndex].dislikes

        if(likeMusic.includes(getUser)) {
          this.setState({ userLikeMusic: true })
        }

        if(dislikeMusic.includes(getUser)) {
          this.setState({ userDislikeMusic: true })
        }

        if(likeMusic.includes(getUser) && dislikeMusic.includes(getUser)) {
          this.setState({ userLikeMusic: false, userDislikeMusic: false })
        }
      }
    }
  }

  onPreviousClick = () => {
    if(this.props.isUserLoggedIn) {
      if(this.state.currentIndex > 0){
        this.setState({ currentIndex: this.state.currentIndex - 1}, this.onPrevOrNextClick)
      } else {
        this.setState({ currentIndex: 0}, this.onPrevOrNextClick)
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
        // TODO: call the backend here to get 5 more music, and set the currentIndex to 0, set musicInfo to new Music

        this.setState({ currentIndex: this.state.currentIndex }, this.onPrevOrNextClick)
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
    let likeMusic = this.state.musicInfo[this.state.currentIndex].likes 
    let dislikeMusic = this.state.musicInfo[this.state.currentIndex].dislikes
    if(likeMusic.includes(this.state.userGoogleId)) {
      this.setState({ userLikeMusic: true })
    } else {
      this.setState({ userLikeMusic: false })
      if(dislikeMusic.includes(this.state.userGoogleId)) {
        this.setState({ userDislikeMusic: true })
      } else {
        this.setState({ userDislikeMusic: false })
      }
    }
  }

  onDislikeClick = () => {
    if(this.props.isUserLoggedIn) {
      this.setState({ userLikeMusic: false, userDislikeMusic: true })

      axios({
        method: 'put',
        url: 'https://q2nypxvh02.execute-api.us-west-1.amazonaws.com/Prod/Users',
        data: {
            CustomerId: this.props.userInfo.googleId,
            dislikes: 'song_id',       
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
          likes: 'song_id',
        }
      })
    } else {
      this.setState({ showModal: true })
    }
  }

  togglePlayPause = () => {
    if(this.props.isUserLoggedIn) {
      console.log("Play")
      this.setState({ playing: !this.state.playing }, this.playPauseAudio)
    } else {
      this.setState({ showModal: true })
    }
  }

  playPauseAudio = () => {
    this.props.currentMusic(this.state.currentIndex)
    let track = this.state.musicInfo[this.state.currentIndex].song_id 
    if(this.state.playing) {
      this.player.src = track 
      this.player.play() 
    } else {
      this.player.pause()
    }
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

          <audio ref={ref => (this.player = ref)}/>
          {this.state.userDislikeMusic ? (<Dislike onDislikeClick={this.onDislikeClick} ButtonOpacity={1}/>) : (<Dislike onDislikeClick={this.onDislikeClick} ButtonOpacity={0.6}/>)}
          <Previous onPreviousClick={this.onPreviousClick}/>
          {this.state.playing ? <Pause onPlayerClick={this.togglePlayPause} /> : <Play onPlayerClick={this.togglePlayPause}/>}
          <Next onNextClick={this.onNextClick}/>
          {this.state.userLikeMusic ? (<Like onLikeClick={this.onLikeClick} ButtonOpacity={1}/>) : (<Like onLikeClick={this.onLikeClick} ButtonOpacity={0.6}/>)}
        </div>
      </footer>
    );
  }
}

export default Player;