import React from "react";

import "./Buttons.css";
// icons from: https://www.iconfinder.com/iconsets/google-material-design-icons

const Play = ({onPlayerClick}) => {
    return (
        <img src={require('./Images/play.png')} alt="play" onClick={onPlayerClick} className="divPadding"/>
    )
}

export default Play;
