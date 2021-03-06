import React, { Component } from 'react';
// import { SpotifyApiContext } from 'react-spotify-api';
import Particles from 'react-particles-js';
import Navigation from './components/Navigation/Navigation';
import Logo from './components/Logo/Logo';
import FaceRecognition from './components/FaceRecognition/FaceRecognition.js';
import ImageLinkForm from './components/ImageLinkForm/ImageLinkForm';
import Rank from './components/Rank/Rank';
import Signin from './components/Signin/Signin.js'
import Register from './components/Register/Register.js'
import SpotifyAPI from './components/Spotify/SpotifyAPI.js'
import './App.css';

const particlesOptions = {
  particles: {
    number: {
      value: 100,
      density: {
        enable: true,
        value_area: 800
      }
    }
  }
}

const initialState = {
    input: '',
    ImageUrl: '',
    box: {},
    route: 'home',
    isSignedIn: true,
    user: {
      id: '',
      name: '',
      email: '',
      entries: 0,
      joined: '',
    }
}

const saveStateLocalStorage = (state) => {
  const serializedState = JSON.stringify(state);
  localStorage.setItem('state', serializedState);
  console.log("SAVE STATE");
  console.log(serializedState);
}

const loadStateLocalStorage = () => {
  const serializedState = localStorage.getItem('state');
  if (serializedState === null) return undefined;
  console.log("LOAD STATE");
  console.log(serializedState);
  return JSON.parse(serializedState);
}

class App extends Component {

  constructor() {
    super();
    const currState = loadStateLocalStorage();
    if (currState === undefined){
      this.state = initialState;
    }else{
      this.state = currState;
    }
  }

  loadUser = (data) => {
    this.setState({user: {
      id: data.id,
      name: data.name,
      email: data.email,
      entries: data.entries,
      joined: data.joined
    }})
    saveStateLocalStorage(this.state);
  }

  calculateFaceLocation = (data) => {
    const clarifaiFace = data.outputs[0].data.regions[0].region_info.bounding_box;
    const image = document.getElementById('inputimage');
    const width = Number(image.width);
    const height = Number(image.height);
    return {
      leftCol: clarifaiFace.left_col * width,
      topRow: clarifaiFace.top_row * height,
      rightCol: width - (clarifaiFace.right_col * width),
      bottomRow: height - (clarifaiFace.bottom_row * height),
    }
  }

  displayFaceBox = (box) => {
    console.log(box);
    this.setState({box: box});
    saveStateLocalStorage(this.state);
  }

  onInputChange = (event) => {
    this.setState({input: event.target.value});
    saveStateLocalStorage(this.state);
  }

  onButtonSubmit = () => {
    this.setState({imageUrl: this.state.input})
      console.log("click");
      fetch('http://localhost:3000/imageurl', {
        method: 'post',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          input: this.state.input
        })
      })
      .then(response => response.json())
      .then(response => {
        if (response){
          fetch('http://localhost:3000/image', {
            method: 'put',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              id: this.state.user.id
            })
          })
          .then(response => response.json())
          .then(count => {
            this.setState(Object.assign(this.state.user, { entries: count }))
          })
          .catch(console.log)
        }
        this.displayFaceBox(this.calculateFaceLocation(response))
      })
      .catch(err => console.log(err));
      saveStateLocalStorage(this.state);
  }

  onRouteChange = (route) => {
    if (route === 'signout'){
      this.setState(initialState)
      this.setState({route: 'signin'})
      window.location.reload(false);
      localStorage.removeItem('state');
      return
    } else if (route === 'home'){
      this.setState({isSignedIn: true})
    }
    this.setState({route: route});
    saveStateLocalStorage(this.state);
  }

  render() {
    const { isSignedIn, imageUrl, route, box } = this.state;
    return (
      <div className="App">
      <Particles className='particles'
        params={particlesOptions} />
        <div className="header">
          <div className="logo">
            <Logo />
          </div>
          <div className="nav">
            <Navigation isSignedIn={isSignedIn} onRouteChange={this.onRouteChange}/>
          </div>
        </div>
        { route === 'home'
            ? <div className="login">
                <div className="rank">
                  <Rank name={this.state.user.name} entries={this.state.user.entries}/>
                </div>

                <div className="imagelinkform">
                  <ImageLinkForm
                    onInputChange={this.onInputChange}
                    onButtonSubmit={this.onButtonSubmit}/>
                </div>
                
              {/*<FaceRecognition box={box} imageUrl={imageUrl}/>*/}
              <SpotifyAPI/>
            </div>
            : (
              this.state.route === 'signin'
              ? <Signin loadUser={this.loadUser} onRouteChange={ this.onRouteChange }/>
              : <Register loadUser={this.loadUser} onRouteChange={ this.onRouteChange }/>
            )
        }
      </div>
    );
  }
}

export default App;
