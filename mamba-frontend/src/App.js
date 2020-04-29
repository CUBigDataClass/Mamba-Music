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
    };

    this.handleChangeRadioIndex = this.handleChangeRadioIndex.bind(this);
  }

  handleChangeRadioIndex(resp) {
    this.props.chooseRadio(resp)
  }

  downLoadSong = () => {
		fetch('https://storage.googleapis.com/mamba_songs_bucket/00818d62-89e1-11ea-b15b-42010a8a0002.mp3')
			.then(response => {
				response.blob().then(blob => {
          console.log("getting the song")
					let url = window.URL.createObjectURL(blob);
          let a = document.createElement('a');
          // console.log(url);
          a.href = url;
					a.download = 'song.mp3';
					a.click();
				});
				//window.location.href = response.url;
		});
  }

  render() {
    return (
      <div className="appContainer">
        <Container fluid>
          <Row>
            <Col md={{ span: 6, offset: 3 }}> 
              <h1 className="musicTitle">{this.props.musicDeets[this.props.currentMusic].title}</h1>
              <br/>
              <div className="imgDiv">
                <img src={this.props.musicDeets[this.props.currentMusic].art_id} alt="Some" className="imageClass"/>
              </div>
              <br/>
              <p className="gaming">{this.props.musicDeets[this.props.currentMusic].artist} - {this.props.musicDeets[this.props.currentMusic].genre}</p>
              <img className="downloadBtn" src={require('./Buttons/Images/download.png')} onClick={this.downLoadSong}></img>
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