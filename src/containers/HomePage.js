import React from 'react';
import axios from 'axios';

import {WelcomeMessage, TaskCardList, TasksStatistics} from '../components';

import { Typography, Space, Row, Col, Tabs , Divider, Progress, List } from 'antd';
const { Title, Paragraph, Text } = Typography;


const getUserTasks = async (user) => {
    // TODO: get user tasks
    await axios.get('/create', {}, {
          user_id: user.id,
          username: user.username,
          first_name: user.first_name,
          last_name: user.last_name,
          photo_url: user.photo_url,
      });
}


class HomePage extends React.Component {

    constructor(props) {
        super(props);
        console.log(props);
        this.state = {tasks: null};
        this.getTasks();
        
    }

    async getTasks() {
        let user_id = localStorage.getItem('user_id')
        await axios.get(`${user_id}/tasks`)
        .then(res => {
            this.setState({
                tasks: res.data
            })
        })
        .catch(err => console.log(err));
    }

    render() {
        if (!this.state.tasks) {
            return <div>Loading..</div>
        }
        return (
        <div className="page" style={{minHeight: '95vh'}}>
            <WelcomeMessage name={this.props.user.first_name} new={this.state.tasks.length == 0}/>
            <TaskCardList tasks={this.state.tasks} colorCodeTags={true} viewGroup={true}/>
            <Divider />
            <TasksStatistics tasks={this.state.tasks} />
        </div>
    );
    }
}

export default HomePage;