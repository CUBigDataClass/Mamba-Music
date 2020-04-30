import React from "react";
import {Container, Row, Col} from "react-bootstrap"

import "./App.css";
import RadioList from "./RadioList";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      mane: false,
      changeRadioIndex: null,
      artistt: {
        melody_rnn: 'Melody RNN',
        performance_rnn: 'Performance RNN',
        polyphony_rnn: 'Polyphony RNN',
        pianoroll_rnn_nade: 'Pianoroll RNN Nade',
        improv_rnn: 'Improv RNN',
        music_vae: 'Music Vae',
        music_transformer: 'Music Transformer'
      }
    };

    this.handleChangeRadioIndex = this.handleChangeRadioIndex.bind(this);
  }

  handleChangeRadioIndex(resp) {
    this.props.chooseRadio(resp)
  }

  downLoadSong = () => {
    let getMusic = 'https://storage.googleapis.com/mamba_songs_bucket/' + this.props.musicDeets[this.props.currentMusic].SongId + '.mp3'
		fetch(getMusic)
			.then(response => {
				response.blob().then(blob => {
					let url = window.URL.createObjectURL(blob);
          let a = document.createElement('a');
          a.href = url;
					a.download = this.props.musicDeets[this.props.currentMusic].title
					a.click();
				});
		});
  }

  render() {
    return (
      <div className="appContainer">
        <Container fluid>
          <Row>
            <Col md={{ span: 6, offset: 3 }}> 
              <div className="imgDiv">
                {this.props.musicDeets[this.props.currentMusic].ArtId && (
                  <img src={'https://storage.googleapis.com/mamba_songs_bucket/' + this.props.musicDeets[this.props.currentMusic].ArtId + '.png'} alt="" className="imageClass"/>
                )} 
                {!this.props.musicDeets[this.props.currentMusic].ArtId && (
                  <img src="https://www.stickpng.com/assets/images/580b57fbd9996e24bc43bf94.png" alt="" className="imageClass"/>
                )}                
              </div>
              <br/>
              <h1 className="musicTitle">{this.props.musicDeets[this.props.currentMusic].title}</h1>
              <p className="gaming">{this.state.artistt[this.props.musicDeets[this.props.currentMusic].artist]}</p>
              <img className="downloadBtn" src={require('./Buttons/Images/download.png')} onClick={this.downLoadSong} alt=""></img>
            </Col>
            <Col md={{ span: 3 }}>
              <RadioList chooseRadio={this.handleChangeRadioIndex}/>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}

export default App;