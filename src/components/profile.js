import React, { useState } from 'react';
import { render } from 'react-dom';
import { Link } from 'react-router-dom';
import 'antd/dist/antd.css';
import axios from 'axios';

import { Avatar } from 'antd';
import { GithubOutlined } from '@ant-design/icons';

import './profile.css'

class Profile extends React.Component {

    state = {};

    constructor() {
        super();
    }

    render () {
        if (!this.props.user) {
            return (
            <div>
                Loading...
            </div>
            );
        }
        return (
            <Link to='/'>
                <div className={ 'profile' }>
                    <Avatar size={40} icon={<img src={this.props.user.photo_url}/>} className={ 'profile-avatar' }/>
                    <span className={ 'profile-name' }>
                        { this.props.user.first_name + ' ' + this.props.user.last_name }
                    </span>
                </div>
            </Link>
        )
    };
}

export default Profile;