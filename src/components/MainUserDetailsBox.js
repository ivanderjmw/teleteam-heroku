import React, { Component } from 'react';

import { Avatar } from "antd";

class MainUserDetailsBox extends Component {
    render () {
        return (
        <div className="main-user-details-box">
            <Avatar className="user-dp" src="https://ca.slack-edge.com/TUYJR8MPW-U013FQL36SG-965175402e9a-512"/> 
            <div className="user-infotext">
                <h3 className="user-full-name">{this.props.fullName}</h3> 
                <h5 className="user-username">{this.props.username}</h5>
            </div>
        </div>  
      );
    }
};

export default MainUserDetailsBox;