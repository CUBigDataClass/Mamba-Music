import React from "react";

import "./Buttons.css";
// icons from: https://www.iconfinder.com/iconsets/google-material-design-icons

const Pause = ({onPlayerClick}) => {
    return (
        <img src={require('./Images/pause.png')} alt="pause" onClick={onPlayerClick} className="divPadding"/>
    )
}

export default Pause;
