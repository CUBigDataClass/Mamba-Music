import React from 'react';
import {
  Button,
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink,
  UncontrolledDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
} from 'reactstrap';
import GoogleLogin from "react-google-login";
import { GoogleLogout } from "react-google-login";
import './nav.css';

import axios from 'axios';

class NavigationBar extends React.Component {
    constructor() {
        super();
        this.state = {
            userDetails: {},
            isUserLoggedIn: false,
            isOpen: false,
            newUser: null,
        }
    }

    componentDidMount() {
        this.updateParent()
    }

    responseGoogle = response => {
        this.setState({ userDetails: response.profileObj, isUserLoggedIn: true }, this.updateParent);
        
        let userID = this.state.userDetails.googleId
        const querystring = require('querystring');
        let getLink = 'https://q2nypxvh02.execute-api.us-west-1.amazonaws.com/Prod/Users?'+ querystring.stringify({ CustomerId: userID })
        
        axios.get(getLink)
        .then((responseGet) => {
            if(responseGet.data.hasOwnProperty("Item")){
                this.setState({newUser: false}, this.updateUser)
            } else {
                this.setState({ newUser: true }, this.updateUser)
            }
        });
    };

    updateUser() {
        if(this.state.newUser === true) {
            axios({
                method: 'put',
                url: 'https://q2nypxvh02.execute-api.us-west-1.amazonaws.com/Prod/Users',
                data: {
                    CustomerId: this.state.userDetails.googleId,
                    first_name: this.state.userDetails.givenName,
                    last_name: this.state.userDetails.familyName,
                }
            })
        } 
    }

    updateParent() {
        this.props.userInfoOne(this.state.isUserLoggedIn);
        this.props.userInfoTwo(this.state.userDetails);
    }

    logout = () => {
        this.setState({isUserLoggedIn: false}, this.updateParent)
    };

    toggle = () => {
        this.setState({ isOpen: !this.state.isOpen })
    }

    render() {
        const {isUserLoggedIn, userDetails} = this.state
        return (
            <div className="goodStyle">
                <div className="navBarGoodStyle">
                    <Navbar light expand="md" className="navBarSticky">
                        <NavbarBrand href="/">Mamba Music</NavbarBrand>
                        <NavbarToggler onClick={this.toggle} />
                        <Collapse isOpen={this.state.isOpen} navbar>
                            <Nav className="mr-auto" navbar>
                            <NavItem>
                                <NavLink href=" https://github.com/CUBigDataClass/Mamba-Music">GitHub</NavLink>
                            </NavItem>
                            </Nav>
                
                            {!isUserLoggedIn && (
                                <GoogleLogin
                                clientId="6217208450-ocnn05njc1f3cb98e5l2b9mn7g2ph68u.apps.googleusercontent.com"
                                buttonText="Login"
                                render={renderProps => (
                                    <Button color="primary" onClick={renderProps.onClick} disabled={renderProps.disabled}>Login</Button>
                                )}
                                onSuccess={this.responseGoogle}
                                onFailure={this.responseGoogle}
                                isSignedIn={true}
                            />
                            )}

                            {isUserLoggedIn && (
                                <UncontrolledDropdown nav inNavbar className="navNoBullet">
                                    <DropdownToggle nav>
                                        <img src={userDetails.imageUrl} alt="user.img" width="30px" className="profilePic"/>
                                    </DropdownToggle>
                                    <DropdownMenu right>
                                        <DropdownItem>
                                            { userDetails.givenName + ' ' + userDetails.familyName }
                                        </DropdownItem>
                                        <DropdownItem divider />
                                        <GoogleLogout
                                            buttonText="Logout"
                                            onLogoutSuccess={this.logout}
                                            render={renderProps => (
                                                <DropdownItem onClick={renderProps.onClick} disabled={this.render.disabled}>
                                                    Log Out
                                                </DropdownItem>
                                            )}
                                        /> 
                                    </DropdownMenu>
                                </UncontrolledDropdown>
                            )}
                
                        </Collapse>
                        </Navbar>
                    </div>
                <div className="navBarPadding"/>
            </div>
        )
    }
}

export default NavigationBar;
