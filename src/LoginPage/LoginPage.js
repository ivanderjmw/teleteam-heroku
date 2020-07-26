import React, { useState } from 'react';
import { render } from 'react-dom';
import axios from 'axios';
import 'antd/dist/antd.css';
import './LoginPage.css'
import TelegramLoginButton from 'react-telegram-login';


const user_data_test = {id: 849634224, first_name: "Ivander", username: "ivanderjmw", photo_url: "https://t.me/i/userpic/320/yejleuVAnqQ5KGFYUvAbnWzDYyyZ5piKZY5sivedixI.jpg", auth_date: 1594046667}

const handleTelegramResponse = response => {
    console.log(response);
};

class LoginPage extends React.Component {

    constructor(props) {
        super(props)
    }

    loginUser = async (user) => {

        await axios.post('authenticate', {
            id: user.id,
            username: user.username,
            first_name: user.first_name,
            last_name: user.last_name,
            photo_url: user.photo_url,
            auth_date: user.auth_date,
            hash: user.hash
        }).then( res => {
            const { history } = this.props;
            axios.patch(user.id, {
                id: user.id,
                username: user.username,
                first_name: user.first_name,
                last_name: user.last_name,
                photo_url: user.photo_url,
                auth_date: user.auth_date,
                hash: user.hash
            })
            this.props.onLogin(res);
            console.log('You are logged in!');
            history.push('/');
        }).catch( res => {
            alert(`Error authenticating! ${res} ${JSON.stringify(user)}`);
        });
    }

    // NOTE: This extra function is now redundant, but could be used for other things
    // in the future.
    handleTelegramResponse = (res) => {
        this.loginUser(res);
    }

    render() {
        return (
            <div id="Login-Page">
                <div className="jumbotron">
                    <img className="jumbotron-logo" src='https://teleteam.herokuapp.com/static/logo_setsil.svg' /> 
                    <div className="container">
                        <h1>Start using Teleteam</h1>
                        <p>A task manager for your Telegram chat groups. Add the bot handle <span style={{fontWeight:'bold'}}>(@teleteam_bot)</span> to your group, or click the link <a href='https://telegram.me/teleteam_bot' target="_blank" style={{background: '#4545F4', borderRadius: '4px', padding: '4px', fontSize: '2ex', color: 'white', fontWeight: 'bold'}}>here</a>.</p>

                        <TelegramLoginButton dataOnauth={this.handleTelegramResponse} botName="teleteam_bot" />
                    </div>
                </div>
            </div>
        );
    }    
};

export default LoginPage;