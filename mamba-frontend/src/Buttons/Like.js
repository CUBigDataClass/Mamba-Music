import React from "react";

import "./Buttons.css";
// icons from: https://www.iconfinder.com/iconsets/google-material-design-icons

const Like = ({onLikeClick, ButtonOpacity}) => {
    return (
        <img src={require('./Images/like.png')} alt="like" onClick={onLikeClick} className="divPadding" style={{ opacity: ButtonOpacity }}/>
    )
}

export default Like;