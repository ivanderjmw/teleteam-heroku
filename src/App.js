import React, { Component } from 'react';
import { BrowserRouter, Route, Switch, Link, useLocation, Redirect } from 'react-router-dom';
import 'antd/dist/antd.css';
import './index.css';
import './App.css';
import axios from 'axios';

import { CreateMeetingButton, CreateTaskButton } from './components';
import { AppLayout, GroupPage, HomePage, SettingsPage } from './containers';
import LoginPage from './LoginPage/LoginPage';

axios.defaults.baseURL = 'https://teleteam.herokuapp.com/api/';

const PrivateRoute = ({ isLoggedIn, ...props }) =>
  isLoggedIn
    ? <Route { ...props } />
    : <Redirect to="/login" />

class Protected extends Component {

  constructor() {
    super();
    this.state = {
      groups:null,
      user:null
    };
    this.updateGroups.bind(this);

    // Set the token as the axios default header
    axios.defaults.headers.common['token'] = localStorage.getItem('token');

    this.getGroups();
    this.getUser();
  }

  getGroups = async () => {
    let user_id = localStorage.getItem('user_id');

    await axios.get(`${user_id}/groups`).then( ({data}) => {
        console.log('Data received from get: ');
        console.log(data);
        if (this.state.data != data) {
          this.setState({
              groups: data
          });
        }
    })
    return
  }

  getUser = () => {
    let user_id = localStorage.getItem('user_id')
    axios.get(`${user_id}`).then( ({data}) => {
        this.setState({
            user: {
                user_id: data.user_id,
                username: data.username,
                first_name: data.first_name ? data.first_name : '',
                last_name: data.last_name ? data.last_name : '',
                photo_url: data.photo_url,
            }
        });
    })
  }

  updateGroups = async () => {
    await this.getGroups();
    console.log(`Got groups: ${JSON.stringify(this.state)}`);
  }

  render () {
    if (!this.state.groups || !this.state.user) {
      return (
      <div>
          Loading...
      </div>
      );
    }
    return (
    <AppLayout groups={this.state.groups} user={this.state.user} updateGroups={this.updateGroups}>  
      <Switch>
        <Route path="/" exact render={props => 
          <HomePage {...props} user={this.state.user} group={this.state.groups} /> 
        }  />
        <Route path="/settings" render={props => 
          <SettingsPage {...props} user_id={localStorage.getItem('user_id')} />
        } /> 
        <Route path="/group" render={props => 
          <GroupPage {...props}
          group={this.state.groups.find( group => new URLSearchParams(this.props.location.search).get("id") == group.id)}
          /> 
        } />
      </Switch>
    </AppLayout>
    )
  }
}

class App extends Component {

  constructor(props) {
    super(props)

    this.handleLogin = this.handleLogin.bind(this)
  }

  state = {
    // TODO: Implement this logged in value INTO LOCAL STORAGE
    loggedIn: this.getLoginStatus(),
  }

  getLoginStatus () {
    try {
      return localStorage.getItem('logged_in') == 'true'
    } catch (error) {
      localStorage.setItem('logged_in', false)
      return false
    }
  }

  // This function is passed on to loginpage.js
  handleLogin = res => {
    localStorage.setItem('logged_in', true);
    this.setState({loggedIn: this.getLoginStatus()});

    // Store userid and token in local storage
    localStorage.setItem('user_id', res.data.user_id);
    localStorage.setItem('token', res.data.token);

  }

  render () {
    return (
        <div className="App">
          <Switch>
            <Route path="/login" render={props => <LoginPage onLogin={this.handleLogin} {...props}/>}/>
            <PrivateRoute isLoggedIn={ this.getLoginStatus() } path="/" component={Protected} />
          </Switch>
        </div>
    );
  }
};

export default App;
