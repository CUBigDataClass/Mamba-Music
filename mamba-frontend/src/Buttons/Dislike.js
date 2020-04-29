import React from "react";

import "./Buttons.css";
// icons from: https://www.iconfinder.com/iconsets/google-material-design-icons

const Dislike = ({onDislikeClick, ButtonOpacity}) => {
    return (
        <img src={require('./Images/dislike.png')} alt="dislike" onClick={onDislikeClick} className="divPadding" style={{ opacity: ButtonOpacity }}/>
    ) 
}

export default  Dislike;