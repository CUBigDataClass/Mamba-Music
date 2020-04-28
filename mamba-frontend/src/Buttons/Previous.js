import React from "react";

import "./Buttons.css";
// icons from: https://www.iconfinder.com/iconsets/google-material-design-icons

const Previous = ({onPreviousClick}) => {
    return (
        <img src={require('./Images/previous.png')} alt="previous" onClick={onPreviousClick} className="divPadding"/>
    )
}

export default Previous;