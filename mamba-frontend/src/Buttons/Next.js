import React from "react";

import "./Buttons.css";
// icons from: https://www.iconfinder.com/iconsets/google-material-design-icons

const Next = ({onNextClick}) => {
    return (
        <img src={require('./Images/next.png')} alt="next" onClick={onNextClick} className="divPadding"/>
    )
}

export default Next;