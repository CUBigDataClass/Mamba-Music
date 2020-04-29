import React from 'react';
import "./RadioList.css"

class RadioList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
          musicPairInfo: [
            ["Melody RNN", "https://media.npr.org/assets/img/2013/10/29/gardiner_haussmann-b7274171073b4700144cbee8f7671a2d052c5a7a-s800-c85.jpg"],
            ["Performance RNN", "https://www.biography.com/.image/t_share/MTE1ODA0OTcxNzMyNjY1ODY5/wolfgang-mozart-9417115-2-402.jpg"],
            ["Polyphony RNN", "https://www.onthisday.com/images/people/pyotr-ilyich-tchaikovsky-medium.jpg"],
            ["Pianoroll RNN Nade", "https://www.biography.com/.image/t_share/MTI2NTgyMzIxOTcyMjU5NDU5/beethoven-600x600jpg.jpg"],
            ["Improv RNN", "https://hughsroomlive.showare.com/uplimage/Elvis.jpg"],
            ["Music Vae", "https://cdn.britannica.com/18/136518-050-CD0E49C6/The-Beatles-Ringo-Starr-Paul-McCartney-George.jpg"],
            ["Music Transformer", "https://static.billboard.com/files/media/01-Eminem-press-by-Craig-McDean-2019-billboard-1548-1024x677.jpg"],
          ]
        }
    }

    render() {
        return (
            <div id="all">
              <h1 className="radTitle">Pick a Radio Station</h1>
              <div className="entireRadList">
                {this.state.musicPairInfo.map((musPair, index1) => (
                  <div className="grid-container" id={index1} key={index1.toString()}>
                    {musPair.map((item, index2) => 
                      <div className="chunk" key={index2.toString()} onClick={() => this.props.chooseRadio(index1)}>
                        {(index2 === 0) && (
                          <div className="itemDetails">
                            <h1 id="listText">{item}</h1>
                          </div>
                        )}

                        {(index2 === 1) && (
                          <div className="itemPic">
                            <img className="musicPic"src={item} alt="Missing music"></img>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
        );
    }
}

export default RadioList;

